import os
import subprocess
import time

import threading
from .routines.parser.piserial import PiSerial as Piserial

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

    def total_sensors(self, data_tuple):
        self.sensors_list = []
        for default_data in data_tuple:
            for unique_data in default_data:
                for x in xrange(1,8):
                    self.join = 'S' + str(x)
                    if unique_data == self.join:
                        self.temp_data = (x,self.join)
                        self.sensors_list.append(self.temp_data)
        return tuple(self.sensors_list)


    def inserting_sensors(self, sensors):
        logging.info('Verifying Sensors table info')
        try:
            with transaction.atomic():
                for sensor in sensors:
                    models.Sensor.objects.update_or_create(name=sensor[0])
        except Exception as e:
            logging.error(e)


    def creating_data_tuple(self, lines):
        print("lines\n")
        print(lines)
        self.brute_data = []
        for line in lines:
            self.temp = line.split(',')
            #for x in range(1,3):
            #    self.temp[x] = float(self.temp[x])
            self.temp[4] = self.temp[4].replace('\r\n','')
            self.brute_data.append(self.temp)
        return self.brute_data

    def inserting_acceleration(self, job, accelerations):
        print('Inserting acceleration parser method')
        try:
            with transaction.atomic():
                for acceleration in accelerations:
                    print('Saving acceleration: ')
                    print(acceleration)
                    sensor = models.Sensor.objects.get(name=acceleration[0])
                    models.Acceleration.objects.create(
                        sensor=sensor,
                        x_value=acceleration[1],
                        y_value=acceleration[2],
                        z_value=acceleration[3],
                        timestamp_ref=acceleration[4],
                        job_id=job
                    )
        except Exception as e:
            print('Exception caught while inserting acceleration ')
            raise e
            logging.error(e)

    def inserting_speed(self, data_tuple):
        logging.info('--> Inserting SPEED Data...')
        self.cur.executemany("INSERT INTO Speed VALUES(?, ?, ?, ?, ?);", data_tuple)
        self.con.commit()
        logging.info('SPEED Data loaded to Database with success!')

    def inserting_amplitude(self, data_tuple):
        logging.info('--> Inserting AMPLITUDE Data...')
        self.cur.executemany("INSERT INTO Amplitude VALUES(?, ?, ?, ?, ?);", data_tuple)
        self.con.commit()
        logging.info('AMPLITUDE Data loaded to Database with success!')

    def inserting_frequency(self, data_tuple):
        logging.info('--> Inserting FREQUENCY Data...')
        self.cur.executemany("INSERT INTO Frequency VALUES(?, ?, ?, ?, ?);", data_tuple)
        self.con.commit()
        logging.info('FREQUENCY Data loaded to Database with success!')


class ParseDataThread(threading.Thread):

    def __init__(self, job=None):
        threading.Thread.__init__(self)
        self.current_job = job

    def set_current_job(self, job):
        self.current_job = job

    def run(self):
        self.parser_routine()

    def parser_routine(self):
        piserial = Piserial()
        piserial.open_serialcom()

        parser = Parser()
        parser.inserting_acceleration(
            self.current_job,
            parser.creating_data_tuple(
                piserial.data_output_list()
            )
        )


class GetSensorsThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.get_sensors_routine()

    def get_sensors_routine(self):

        piserial = Piserial()
        piserial.open_serialcom()

        parser = Parser()
        parser.inserting_sensors(
            parser.creating_data_tuple(
                piserial.data_output_list()))


class CollectData:

    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = CollectData()
        return cls.instance

    def __init__(self):
        # Start the thread setting the first job
        self.current_thread = ParseDataThread(1)

    def collect(self, job, start_experiment=False):
        if start_experiment:
            print('First Job -> Starting parser thread...')
            self.current_thread.start()
        else:
            print('Changing parser thread to job ' + str(job))
            self.current_thread.set_current_job(job)

    def get_sensors(self):
        get_sensors_thread = GetSensorsThread()
        get_sensors_thread.start()
        return get_sensors_thread

def insert_command(data, begin_experiment_flag=False):
    print('\nSending this data to serial port: ' + data)
    piserial = Piserial()
    piserial.open_serialcom()
    if(begin_experiment_flag):
        print('Start experiment flag setted...')
        piserial.data_input('-1')
    time.sleep(0.5)
    piserial.data_input(data)
    piserial.close_serialcom()

def set_job_frequency(frequency, first_job=False):
    try:
        insert_command(frequency, first_job)
    except RoutineException as e:
        raise e

