import os
import subprocess

import threading
from .routines.parser.piserial import PiSerial as Piserial
from sensor_data.exceptions import RoutineException

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
        self.brute_data = []
        for line in lines:
            self.temp = line.split(',')
            for x in range(1,3):
                self.temp[x] = float(self.temp[x])
            self.temp[4] = self.temp[4].replace('\r\n','')
            self.brute_data.append(self.temp)
        return self.brute_data

    def inserting_acceleration(self, data_tuple):
        logging.info('--> Inserting ACCELERATION Data...')
        self.cur.executemany("INSERT INTO Acceleration VALUES(?, ?, ?, ?, ?);", data_tuple)
        self.con.commit()
        logging.info('ACCELARATION Data loaded to Database with success!')

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


class RoutineUtils(threading.Thread):

    def __init__(self, mode=False):
        threading.Thread.__init__(self)
        self.mode = mode

    def run(self):
        if self.mode:
            # Read data mode
            self.parser_routine()
        else:
            # Get sensors mode
            self.get_sensors_routine()

    def parser_routine():

        piserial = Piserial()
        piserial.open_serialcom()

        parser = Parser()
        parser.inserting_acceleration(
            parser.creating_data_tuple(
                piserial.data_output_list()))

def get_sensors_routine():

    piserial = Piserial()
    piserial.open_serialcom()

    parser = Parser()
    parser.inserting_sensors(
        parser.creating_data_tuple(
            piserial.data_output_list()))

def insert_command(data, begin_experiment_flag=False):
    print('DADO QUE VAI PRA PORTA SERIAL:')
    print(data)
    print(type(data))
    piserial = Piserial()
    piserial.open_serialcom()
    if(begin_experiment_flag):
        piserial.data_input('-1')
    piserial.data_input(data)
    piserial.close_serialcom()

def set_job_frequency(frequency, first_job=False):
    try:
        insert_command(frequency, first_job)
    except RoutineException as e:
        raise e

