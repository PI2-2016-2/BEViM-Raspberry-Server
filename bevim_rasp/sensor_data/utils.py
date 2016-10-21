import os
import subprocess

import threading
from .routines.parser.parser import ParserData as Parser
from .routines.parser.piserial import PiSerial as Piserial
from sensor_data.exceptions import RoutineException

from .exceptions import RoutineException
from bevim_rasp.settings import BASE_DIR

# RESPONSE CODES
CONTROL_INTEGRATE_ERROR = 500
SUCCESS = 200

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

def inserting_command(frequency, begin_experiment_flag=False):
    piserial = Piserial()
    piserial.open_serialcom()
    if(begin_experiment_flag):
        piserial.data_input('-1')
    piserial.data_input(frequency)
    piserial.close_serialcom()

def set_job_frequency(frequency):
    try:
        inserting_command(frequency)
    except RoutineException as e:
        raise e

