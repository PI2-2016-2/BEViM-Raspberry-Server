#!/usr/bin/python

import serial, time
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
        print('\nReaded line not decoded: ')
        print(line)
        output = line.decode('utf-8')
        return output

    def data_output_list(self, notify_obj=None):
        self.data_list = []
        i = 0
        while True:
            incoming_data = self.data_output()
            print('\n i = ' + str(i) +  ' - Readed line decoded: ' + incoming_data)
            if not incoming_data:
                if i > 5:
                    break
            if incoming_data:
                self.data_list.append(incoming_data)
            if i is 3:
                if notify_obj:
                    notify_obj.notify_started()
                    notify_obj = None
            i += 1
        self.close_serialcom()
        return self.data_list

    def data_input(self,data):
        data = (data + '\n').encode('utf-8')
        self.bytes_writen = self.ser.write(data)
