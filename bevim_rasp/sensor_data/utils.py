import os
import subprocess, requests, json
import serial, sys, time, re

from threading import Thread

from . import protocol
from .exceptions import RoutineException
from bevim_rasp.settings import BASE_DIR

from sensor_data import models
from django.db import transaction, connection, IntegrityError
import logging

from bitstring import BitArray, Bits

# RESPONSE CODES
CONTROL_INTEGRATE_ERROR = 500
SUCCESS = 200


class Parser:

    logging.basicConfig(format='%(asctime)s %(message)s', filename='parser.log', level=logging.INFO, datefmt='%d/%m/%Y %I:%M:%S %p')

    def inserting_sensors(self, sensors):
        logging.info('Verifying Sensors table info')
        try:
            with transaction.atomic():
                # Deleting all the saved sensors to save only the active ones
                models.Sensor.objects.all().delete()
                for sensor in sensors:
                    models.Sensor.objects.create(name=sensor)
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


class PiSerial:

    FAIL_TO_OPEN = 500

    def __init__(self):
        self.initialization()

    def initialization(self):
        self.port = '/dev/ttyACM0'
        self.baudrate = 9600
        self.timeout = 1
        self.current_timestamp = 0
        self.sensors_data = {}
        self.initialize_collect_sensors_variables()

    def initialize_collect_sensors_variables(self):
        for sensor in models.Sensor.objects.all():
            self.sensors_data[sensor.name] = {}
        self.frequencies = {}

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

    def read_active_sensors(self, notify_obj=None):
        print("Reading active sensors...")
        i = 0
        while True:
            sensors = self.ser.read()
            print(str(i) + " Read sensors: " + str(sensors))

            if sensors or i is 10:
                break

            if i is 1: # Waiting 2 loops to set the thread started
                if notify_obj:
                    notify_obj.notify_started()
                    notify_obj = None
            i += 1
        bits = BitArray(sensors)
        i = 8
        active_sensors = []
        for active in bits:
            if active:
                active_sensors.append(i)
            i -= 1
        return active_sensors

    def read_sensor_data(self):
        header = self.ser.read()
        print("HEADER IN BYTES %s " % str(header))
        if header:

            header = BitArray(header)

            if header.uint is protocol.TIMESTAMP_HEADER:
                print("TIMESTAMP HEADER")
                timestamp = self.ser.read(protocol.TIMESTAMP_BYTES_QUANTITY)
                print("TIMESTAMP VALUE IN BYTES %s " % str(timestamp))
                timestamp = BitArray(timestamp).uint
                self.current_timestamp = timestamp

                print("TIMESTAMP VALUE %s " % self.current_timestamp)
            elif header.uint is protocol.FREQUENCY_FLAG_HEADER:
                print("FREQUENCY REACHED HEADER")
                frequency_in_bytes = self.ser.read(protocol.FREQUENCY_BYTES_QUANTITY)
                frequency = BitArray(frequency_in_bytes).uint
                CurrentFrequency.get_instance().update(frequency, system_status=True)
                self.frequencies[str(self.current_timestamp)] = frequency
            else:
                print("SENSOR HEADER")
                sensor_number = header[0:4].uint
                sensor_axis = header[4:8].uint

                if protocol.validate_sensor_number_and_axis(sensor_number, sensor_axis):
                    print("Sensor number %s; Sensor axis %s" % (sensor_number, sensor_axis) )
                    axis_value = self.ser.read(protocol.SENSOR_BYTES_QUANTITY)

                    print("\n\n\AXIS VALUE: " + str(axis_value) + "\n\n")
                    if axis_value:
                        # ENABLE THIS DIVISION IF USING ACCELEROMETER
                        axis_value = Bits(axis_value).int / protocol.SENSOR_LSB_RESOLUTION
                        # axis_value = Bits(axis_value).int

                        sensor_number = str(sensor_number)

                        if self.current_timestamp in self.sensors_data[sensor_number]:
                            sensor_data = self.sensors_data[sensor_number][self.current_timestamp]
                        else:
                            sensor_data = [sensor_number, -1, -1, -1, -1]

                        sensor_data[sensor_axis] = axis_value

                        # The last position of the result list ([S!, 10, 10, 10, 123042]) is the timestamp
                        sensor_data[-1] = self.current_timestamp

                        self.sensors_data[sensor_number][self.current_timestamp] = sensor_data

                else:
                    print("\n SENSOR BYTE WITH ERROR: Sensor number %s ; Axis %s \n" % (sensor_number, sensor_axis))
                    time.sleep(3)


    def data_output_list(self, notify_obj=None):

        i = 0
        while True:
            try:
                self.read_sensor_data()
            except serial.SerialException as e:
                raise RoutineException(250, aditional_exception=e)

            if self.current_timestamp > 4000:
                break

            if i is 1:
                if notify_obj:
                    notify_obj.notify_started()
                    notify_obj = None
            i += 1

        return {
            'sensors': self.sensors_data,
            'frequencies': self.frequencies
        }

    def data_input(self, data):
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
            piserial.read_active_sensors(notify_obj)
        )

    @classmethod
    @with_serial_open
    def parser_routine(cls, notify_obj=None, piserial=None, jobs_info=None):

        try:
            print("Getting data")
            data = piserial.data_output_list(notify_obj)
        except RoutineException as e:
            # Communicate that system is down
            CurrentFrequency.get_instance().update(system_status=False)
        else:
            sensors_data = []
            for data_list in data['sensors'].values():
                for sensor_data in data_list.values():
                    sensors_data.append(sensor_data)

            parser = Parser()
            sensor_data_with_job_ids = parser.add_jobs_ids(sensors_data, jobs_info)

            print(len(sensor_data_with_job_ids))

            send_accelerations(json.dumps({
                'sensors': sensor_data_with_job_ids,
                'frequencies': data['frequencies']
            }))

class CurrentFrequency:

    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = CurrentFrequency()
        return cls.instance

    def __init__(self):
        self.current_frequency = -1
        self.system_status = True

        # Used for simulation
        self.already_lauched = False

    def get(self):
        return (self.current_frequency, self.system_status)

    def update(self, new_frequency=None, system_status=False):
        if new_frequency is not None:
            print("Updating current frequency to %s Hz." % new_frequency)
            self.current_frequency = new_frequency
        self.system_status = system_status

        # self.system_status = True # REMOVE THIS
        # self.__simulate_waiting_for_frequency(new_frequency)

    def __simulate_waiting_for_frequency(self, new_frequency):
        if(not self.already_lauched):
            increment_thread = Thread(
                target=self.__stub_increment_frequency,
                kwargs={'frequency': new_frequency}
            )
            increment_thread.start()
            self.already_lauched = True

    def __stub_increment_frequency(self, frequency=0):
        while self.current_frequency < frequency:
            self.current_frequency += 4
            print("Frequency updated to %s Hz" % self.current_frequency)
            time.sleep(1)

    @classmethod
    def clean(cls):
        cls.instance = None

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
    if type(data) is not bytes:
        data = bytes([int(data)])
    piserial = PiSerial()
    piserial.open_serialcom()
    if(begin_experiment_flag):
        print('Start experiment flag setted. Sending -1 to serial port...')
        piserial.data_input(protocol.START_EXPERIMENT_FLAG)
    time.sleep(0.1)
    print('\nSending this data to serial port: ' + str(data) + " - " + str(Bits(data).int))
    piserial.data_input(data)
    piserial.close_serialcom()

def send_accelerations(data):
    application_url = "http://localhost:8000/bevim/receive_result"
    headers = {'content-type': 'application/json'}
    response = requests.put(application_url, data=data, headers=headers)
    print (response)
