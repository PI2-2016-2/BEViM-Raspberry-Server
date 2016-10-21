#!/usr/bin/python

import time
import threading

from sensor_data.exceptions import RoutineException

class routine(threading.Thread):

    def __init__(self, frequency, start_flag=False, mode=1):
        threading.Thread.__init__(self)
        self.frequency = frequency
        self.start_flag = start_flag
        self.mode = mode

    def run(self):
        if self.mode is 1:
            # Read mode
            parser_routine()
        elif self.mode is 2:
            # Get sensors mode
            get_sensors_routine()
        else:
            inserting_command(self.frequency, self.start_flag)

#Rotina responsavel por pegar os sensores ativos - FALTA TESTAR
def get_sensors_routine():

    #Instanciacao da porta serial
    piserial = Piserial()
    piserial.open_serialcom()

    #Instanciacao do parser e definicao dos sensores
    parser = Parser()
    parser.inserting_sensors(
        parser.total_sensors(
            parser.creating_data_tuple(0,
                piserial.data_output_list())))

def parser_routine():

    piserial = Piserial()
    piserial.open_serialcom()

    parser = Parser()
    parser.inserting_acceleration(
        parser.creating_data_tuple(1,
            piserial.data_output_list()))

    print '--> Finishing Parser Routine!'

#Funcao para teste da rotina de Parser
def inserting_command(frequency, begin_experiment_flag=False):

    piserial = Piserial()

    try:
        piserial.open_serialcom()
    except RoutineException, e:
        raise e
    else:
        if(begin_experiment_flag):
            piserial.data_input('-1')

        piserial.data_input(frequency)
        piserial.close_serialcom()
