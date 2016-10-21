#!/usr/bin/python

import sqlite3
import logging

class ParserData:

    logging.basicConfig(format='%(asctime)s %(message)s', filename='parser.log', level=logging.INFO, datefmt='%d/%m/%Y %I:%M:%S %p')

    def __init__(self):
        self.connect_DB()
        self.schema()

    def connect_DB(self):
        self.con = sqlite3.connect('sensor_data.db')
        self.cur = self.con.cursor()
        logging.info('... Database connected ...')

    def schema(self):
        logging.info('... Verifying Schema ...')
        self.info = self.cur.execute('PRAGMA table_info(Sensor)')
        if len(self.info.fetchall()) == 0:
            self.cur.execute('CREATE TABLE Sensor(sensor_id INTEGER PRIMARY KEY NOT NULL,'
                                                                             'name VARCHAR(3))')
            self.cur.execute('CREATE TABLE Acceleration(sensor_id INTEGER NOT NULL,'
                                                                                     'acceleration_x DECIMAL(2,2),'
                                                                                     'acceleration_y DECIMAL(2,2),'
                                                                                     'acceleration_z DECIMAL(2,2),'
                                                                                     'timestamp INTEGER,'
                                                                                     'FOREIGN KEY(sensor_id) REFERENCES Sensor(sensor_id))')
            self.cur.execute('CREATE TABLE Speed(sensor_id INTEGER NOT NULL,'
                                                                            'speed_x DECIMAL(2,2),'
                                                                            'speed_y DECIMAL(2,2),'
                                                                            'speed_z DECIMAL(2,2),'
                                                                            'timestamp INTEGER,'
                                                                            'FOREIGN KEY(sensor_id) REFERENCES Sensor(sensor_id))')
            self.cur.execute('CREATE TABLE Amplitude(sensor_id INTEGER NOT NULL,'
                                                                                  'amplitude_x DECIMAL(2,2),'
                                                                                  'amplitude_y DECIMAL(2,2),'
                                                                                  'amplitude_z DECIMAL(2,2),'
                                                                                  'timestamp INTEGER,'
                                                                                  'FOREIGN KEY(sensor_id) REFERENCES Sensor(sensor_id))')
            self.cur.execute('CREATE TABLE Frequency(sensor_id INTEGER NOT NULL,'
                                                                                  'frequency_x DECIMAL(2,2),'
                                                                                  'frequency_y DECIMAL(2,2),'
                                                                                  'frequency_z DECIMAL(2,2),'
                                                                                  'timestamp INTEGER,'
                                                                                  'FOREIGN KEY(sensor_id) REFERENCES Sensor(sensor_id))')
            logging.info('Database schema created with success!')
        else:
            logging.info('Database schema already exists!')

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


    def inserting_sensors(self, sensors_tuple):
        logging.info('Verifying Sensors table info')
        if len(self.cur.execute('SELECT * FROM Sensor').fetchall()) == 0:
            self.cur.executemany("INSERT INTO Sensor VALUES(?, ?);", sensors_tuple)
            self.con.commit()
            logging.info('Information about ACTIVE sensors were inserted with success!')
        else:
            logging.info('Information about ACTIVE sensors already exists!')

    def creating_data_tuple(self, flag, lines):
        self.brute_data = []
        for line in lines:
            self.temp = line.split(',')
            if flag == 1:
                self.verification_sensor_number(self.temp[0])
                self.temp[0] = self.v1
            for x in xrange(1,3):
                self.temp[x] = float(self.temp[x])
            self.temp[4] = self.temp[4].replace('\r\n','')
            self.brute_data.append(tuple(self.temp))
        return tuple(self.brute_data)

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

    def verification_sensor_number(self, value):
        self.split_temp = list(value)
        self.v1 = int(self.split_temp[1])
