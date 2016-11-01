import os
import subprocess
import serial, sys, time

from threading import Thread, current_thread
from concurrent.futures import ThreadPoolExecutor

from . import protocol
from .exceptions import RoutineException
from bevim_rasp.settings import BASE_DIR

from sensor_data import models
from django.db import transaction
import logging
import sqlite3


# RESPONSE CODES
CONTROL_INTEGRATE_ERROR = 500
SUCCESS = 200


class Parser:

    logging.basicConfig(format='%(asctime)s %(message)s', filename='parser.log', level=logging.INFO, datefmt='%d/%m/%Y %I:%M:%S %p')

    def inserting_sensors(self, sensors):
        logging.info('Verifying Sensors table info')
        try:
            with transaction.atomic():
                for sensor in sensors:
                    models.Sensor.objects.update_or_create(name=sensor[0])
        except Exception as e:
            logging.error(e)


    def creating_data_tuple(self, lines):
        self.brute_data = []
        for line in lines:
            self.temp = line.split(',')
            #for x in range(1,3):
            #    self.temp[x] = float(self.temp[x])
            self.temp[4] = self.temp[4].replace('\r\n','')
            self.brute_data.append(self.temp)
        return self.brute_data

    def inserting_acceleration(self, accelerations):
        print('Inserting acceleration parser method')
        try:
            with transaction.atomic():
                print('Saving accelerations:')
                i = 0
                for acceleration in accelerations:
                    print('Saving acceleration ' + str(i))
                    print(acceleration)
                    sensor = models.Sensor.objects.get(name=acceleration[0])
                    models.Acceleration.objects.create(
                        sensor=sensor,
                        x_value=acceleration[1],
                        y_value=acceleration[2],
                        z_value=acceleration[3],
                        timestamp_ref=acceleration[4],
                        job_id=1 # REMOVE THIS - JUST TO TEST
                    )
                    i += 1
        except Exception as e:
            print('Exception caught while inserting acceleration ')
            print(type(e))
            print(e)
            raise e
            logging.error(e)


class PiSerial:

    FAIL_TO_OPEN = 500

    def __init__(self):
        self.initialization()

    def initialization(self):
        self.port = '/dev/ttyACM0'
        self.baudrate = 9600
        self.timeout = 1

    def open_serialcom(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print('Serial port open with success!')
        except serial.SerialException as e:
            raise RoutineException(self.FAIL_TO_OPEN, aditional_exception=e)

    def close_serialcom(self):
        self.ser.close()
        if self.ser.isOpen():
            print('Error in closing the port. Maybe something is stuck?')
        else:
            print('Port closed with success')

    def data_output(self):
        line = self.ser.readline()
        output = line.decode('utf-8')
        return output

    def data_output_list(self, notify_obj=None, save_at_each=False):
        self.data_list = []
        i = 0
        while True:
            incoming_data = self.data_output()
            splitted = incoming_data.split(',')
            if incoming_data:
                if 4 < len(splitted):
                    try:
                        timestamp = float(splitted[4])
                        if timestamp >= 20000:
                            break
                    except Exception as e:
                        print(e)

            print('i = ' + str(i) +  ' - Readed line decoded: ' + incoming_data)
            if not incoming_data:
                if i > 5:
                    break

            if incoming_data:
                self.data_list.append(incoming_data)
                if save_at_each:
                    SerialFacade.save_data_from_serial(incoming_data)

            if i is 3:
                if notify_obj:
                    notify_obj.notify_started()
                    notify_obj = None
            i += 1
        #self.close_serialcom()
        return self.data_list

    def data_input(self,data):
        data = (data + '\n').encode('utf-8')
        self.bytes_writen = self.ser.write(data)


class Routine:

    def with_serial_open(function):
        def decorator(*args, **kwargs):
            piserial = PiSerial()
            piserial.open_serialcom()
            kwargs['piserial'] = piserial
            function(*args, **kwargs)
        return decorator

    @classmethod
    @with_serial_open
    def get_sensors_routine(cls, notify_obj=None, piserial=None):
        parser = Parser()
        parser.inserting_sensors(
            parser.creating_data_tuple(
                piserial.data_output_list(notify_obj)
            )
        )

    @classmethod
    @with_serial_open
    def parser_routine(cls, notify_obj=None, piserial=None):
        # parser = Parser()
        # parser.inserting_acceleration(
            # parser.creating_data_tuple(
        piserial.data_output_list(notify_obj, True)
            # )
        # )

    @classmethod
    @with_serial_open
    def parse_at_each_routine(cls, data, piserial=None):
        print('\t Thread -> ' + current_thread().name)
        parser = Parser()
        parser.inserting_acceleration(
            parser.creating_data_tuple([data])
        )


class SaveSensorDataPool():
    """
        Singleton class to manage the pool of threads to save sensor data
    """

    MAX_THREADS = 8
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = SaveSensorDataPool()
        return cls.instance

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_THREADS)

    def save(self, data):
        self.executor.submit(Routine.parse_at_each_routine, data)


class SerialFacade:
    """
    Interface to receive all collect data from serial port requests
    """

    class NotifyStartedTool:
        """
        Tool to notify if a thread have started
        """
        def __init__(self, started=False):
            self.started = started

        def notify_started(self):
            print('Notifying that thread have started...')
            self.started = True

        def notify_not_started(self):
            print('Notifying that thread have not started...')
            self.started = False

        def is_started(self):
            return self.started

        def wait_start(self):
            print("Waiting for thread start...")
            while(not self.is_started()):
                pass
            #time.sleep(2)
            print("Thread started, keeping on...")

    @classmethod
    def stop_experiment(cls):
        insert_command(protocol.STOP_EXPERIMENT_FLAG)

    @classmethod
    def set_frequency(cls, frequency, start_experiment):
        cls.collect_sensors_data(start_experiment)
        set_job_frequency(frequency, start_experiment)

    @classmethod
    def collect_sensors_data(cls, start_experiment):
        if start_experiment:
            notify_obj = cls.NotifyStartedTool()
            collect_data_thread = Thread(
                target=Routine.parser_routine,
                kwargs={'notify_obj': notify_obj}
            )
            # Start thread to get sensors
            collect_data_thread.start()
            # Waiting for thread start
            notify_obj.wait_start()

    @classmethod
    def get_available_sensors(cls):
        notify_obj = cls.NotifyStartedTool()
        get_sensors_thread = Thread(
            target=Routine.get_sensors_routine,
            kwargs={'notify_obj': notify_obj}
        )

        # Start thread to get sensors
        get_sensors_thread.start()
        # Waiting for thread start
        notify_obj.wait_start()
        # Sending flag to retrieve sensors to control system
        insert_command(protocol.GET_AVAILABLE_SENSORS_FLAG)
        # Waiting get sensors routine save the data to exit main thread
        get_sensors_thread.join()

    @classmethod
    def save_data_from_serial(cls, data):
        SaveSensorDataPool.get_instance().save(data)

def insert_command(data, begin_experiment_flag=False):
    piserial = PiSerial()
    piserial.open_serialcom()
    if(begin_experiment_flag):
        print('Start experiment flag setted. Sending -1 to serial port...')
        piserial.data_input(protocol.START_EXPERIMENT_FLAG)
    time.sleep(0.1)
    print('\nSending this data to serial port: ' + data)
    piserial.data_input(data)
    piserial.close_serialcom()

def set_job_frequency(frequency, first_job=False):
    try:
        insert_command(frequency, first_job)
    except RoutineException as e:
        raise e
