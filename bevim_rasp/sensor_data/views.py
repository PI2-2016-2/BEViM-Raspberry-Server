from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Acceleration, Sensor, Speed, Amplitude, Frequency
from . import utils
from .serializers import SensorSerializer, DataSerializer
from .exceptions import RoutineException

import time


class SensorRestV1(APIView):

    EXPERIMENT_START_FREQUENCY = '-2'

    def get(self, request=None, format=None):
        sensors = Sensor.objects.all()
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if data and (data['value'] == self.EXPERIMENT_START_FREQUENCY):
            response = self.get_sensors_quantity()
        else:
            response = Response(data)
        return response

    def get_sensors_quantity(self):
        """ Method to consult the table to check the present sensors """
        get_sensors_thread = utils.CollectData.get_instance().get_sensors()
        time.sleep(1)  # Waiting a time to the thread start
        utils.insert_command(self.EXPERIMENT_START_FREQUENCY)
        get_sensors_thread.join()
        return self.get()


class AccelerationRestV1(APIView):

    def get(self, request, format=None):
        accelerations = Acceleration.objects.all()
        serializer = DataSerializer(accelerations, many=True)
        return Response(serializer.data)


class SpeedRestV1(APIView):

    def get(self, request, format=None):
        speeds = Speed.objects.all()
        serializer = DataSerializer(speeds, many=True)
        return Response(serializer.data)


class AmplitudeRestV1(APIView):

    def get(self, request, format=None):
        amplitudes = Amplitude.objects.all()
        serializer = DataSerializer(amplitudes, many=True)
        return Response(serializer.data)


class FrequencyRestV1(APIView):

    def get(self, request, format=None):
        frequencies = Frequency.objects.all()
        serializer = DataSerializer(frequencies, many=True)
        return Response(serializer.data)

class ControlRestV1(APIView):

    def post(self, request, format=None):
        """
        This method is used to change the frequency of the table
        """
        job = request.data['job']
        print("Change frequency service called for Job Nº" + job)
        frequency = request.data['frequency']
        try:
            start_experiment = False
            if job is '1':
                # If is the first job, set the start experiment flag to true
                start_experiment = True
            utils.CollectData.get_instance().collect(job, start_experiment)
            time.sleep(3) # Waiting a time to the thread start
            utils.set_job_frequency(frequency, start_experiment)

            status_code = 200
        except RoutineException as exception:
            status_code = exception.error_code

        return HttpResponse(status=status_code)
