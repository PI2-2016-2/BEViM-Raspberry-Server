#!/usr/bin/python

import serial
import _thread as thread
import sys
from sensor_data.exceptions import RoutineException

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
        except serial.SerialException as e:
            raise RoutineException(self.FAIL_TO_OPEN, aditional_exception=e)

    def close_serialcom(self):
        self.ser.close()
        if self.ser.isOpen():
            print('Error in closing the port. Maybe something is stuck?')
        else:
            print('Port closed with success')

    def data_output(self):
        self.output = self.ser.readline()
        return self.output

    def data_output_list(self):
        self.data_list = []
        while True:
            self.incoming_data  = (self.data_output()).decode('utf-8')
            if not self.incoming_data:
                break
            self.data_list.append(self.incoming_data)
        self.close_serialcom()
        return self.data_list

    def data_input(self,data):
        data = (data + '\n').encode('utf-8')
        self.bytes_writen = self.ser.write(data)
