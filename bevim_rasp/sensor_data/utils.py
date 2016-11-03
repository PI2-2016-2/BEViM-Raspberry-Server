import os
import subprocess
import serial, sys, time, re

from threading import Thread

from . import protocol
from .exceptions import RoutineException
from bevim_rasp.settings import BASE_DIR

from sensor_data import models
from django.db import transaction, connection, IntegrityError
import logging


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
    
    def get_job_elapsed_time(self, jobs, job):
        time = 0
        for i in range(1, (int(job) + 1)):
            time += int(jobs[str(i)]['time'])
        return time*1000 # In milliseconds

    def add_jobs_ids(self, data, jobs_info):
        jobs = jobs_info['jobs']
        for acceleration in data:
            timestamp = float(acceleration[4])
            for job_num, job in jobs.items():
                cur_job_time = int(job['time'])*1000
                job_finish_time = self.get_job_elapsed_time(jobs, job_num)
                job_start_time = job_finish_time - cur_job_time
                if job_num == '1':
                    if(timestamp >= job_start_time and timestamp <= job_finish_time):
                        acceleration.append(job['job_pk'])
                        break
                else:
                    if(timestamp > job_start_time and timestamp <= job_finish_time):                
                        acceleration.append(job['job_pk'])
                        break
        return data

    def creating_data_tuple(self, lines):
        brute_data = []
        sensor_data_pattern = protocol.get_sensor_data_pattern()
        for line in lines:
            try:
                sensor_data = sensor_data_pattern.match(line)
                if sensor_data: 
                    brute_data.append(list(sensor_data.groups()))
                else:
                    print("Line readed with problem: '" + str(line) + "'")
            except Exception as e:
                print(e)

        return brute_data


    def inserting_acceleration(self, accelerations):
        from datetime import datetime
        time = datetime.now().time()
        print('Time that stopped reading: ' + str(time))
        print('Inserting accelerations...')
        data_tuple = []
        for acceleration in accelerations:
            sensor = models.Sensor.objects.get(name=acceleration[0])
            acceleration[0] = str(sensor.pk)
            data_tuple.append(tuple(acceleration))

        query = ("INSERT INTO sensor_data_acceleration (sensor_id, x_value, y_value, z_value, timestamp_ref, job_id) VALUES (%s,%s,%s,%s,%s,%s);")
        DatabaseUtils.execute_query("START TRANSACTION;")
        DatabaseUtils.execute_query(query, data_tuple)
        time = datetime.now().time()
        print ("Acceleration data insertion finished in: " + str(time))

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
        if line:
            output = line.decode('utf-8')
        else:
            output = False
        return output

    def data_output_list(self, notify_obj=None):
        self.data_list = []
        i = 0
        pattern = protocol.get_sensor_data_pattern()
        while True:
            incoming_data = self.data_output()
            if incoming_data:
                sensor_data = pattern.match(incoming_data)
                if sensor_data:
                    self.data_list.append(incoming_data)
                    timestamp = float(sensor_data.groups()[4])
                    if timestamp >= 20000:
                        break
                #else:
                    #problems.append(incoming_data)
                    #print("Line readed with problem: '" + str(incoming_data) + "'")

            #print('i = ' + str(i) +  ' - Readed line decoded: ' + incoming_data)
            if not incoming_data:
                if i > 5:
                    break
            
            if i is 3:
                if notify_obj:
                    notify_obj.notify_started()
                    notify_obj = None
            i += 1
        #self.close_serialcom()
        #with open ('problems', 'a') as f: [f.write(p) for p in problems]
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
        print('On get sensors routine...')
        parser = Parser()
        parser.inserting_sensors(
            parser.creating_data_tuple(
                piserial.data_output_list(notify_obj)
            )
        )

    @classmethod
    @with_serial_open
    def parser_routine(cls, notify_obj=None, piserial=None, jobs_info=None):
        parser = Parser()
        data = piserial.data_output_list(notify_obj)
        data_list = parser.creating_data_tuple(data)
        data_with_job_ids = parser.add_jobs_ids(data_list, jobs_info)
        parser.inserting_acceleration(data_with_job_ids)


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
            print("Thread started, keeping on...")

    @classmethod
    def stop_experiment(cls):
        insert_command(protocol.STOP_EXPERIMENT_FLAG)

    @classmethod
    def set_frequency(cls, frequency, start_experiment, jobs_info):
        cls.collect_sensors_data(start_experiment, jobs_info)
        insert_command(frequency, start_experiment)

    @classmethod
    def collect_sensors_data(cls, start_experiment, jobs_info):
        if start_experiment:
            notify_obj = cls.NotifyStartedTool()
            collect_data_thread = Thread(
                target=Routine.parser_routine,
                kwargs={'notify_obj': notify_obj, 'jobs_info': jobs_info}
            )
            # Start thread to get sensors
            collect_data_thread.start()
            # Waiting for thread start
            notify_obj.wait_start()

    @classmethod
    def get_available_sensors(cls):
        print('Getting available sensors')
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


class DatabaseUtils:
    
    def execute_query(query, data_tuple=False):
        with connection.cursor() as cursor:
            try:
                if data_tuple:
                    cursor.executemany(query, data_tuple)
                else:
                    cursor.execute(query)
                connection.commit()
            except:
                raise IntegrityError

