import os
import subprocess

from .exceptions import RoutineException
from bevim_rasp.settings import BASE_DIR

# RESPONSE CODES
CONTROL_INTEGRATE_ERROR = 500 
SUCCESS = 200

class RoutineUtils:

    def set_job_frequency(self, frequency):
        command = BASE_DIR + "/sensor_data/routines/control_routine " + str(frequency)
        result = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE)
        
        result = str(result.stdout.read())
        expected_response = "Response({0})".format(SUCCESS)
        if not expected_response in result:
            raise RoutineException(500, "Error to send data to control system.")