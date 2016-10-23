from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Acceleration, Sensor, Speed, Amplitude, Frequency
from . import utils, protocol
from .serializers import SensorSerializer, DataSerializer
from .exceptions import RoutineException

import time


class SensorRestV1(APIView):

    def get(self, request=None, format=None):
        sensors = Sensor.objects.all()
        print(sensors)
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if data and (data['value'] == protocol.GET_AVAILABLE_SENSORS_FLAG):
            response = self.get_sensors_quantity()
        else:
            response = Response(data)
        return response

    def get_sensors_quantity(self):
        """ Method to consult the table to check the present sensors """
        utils.SerialFacade.get_available_sensors()
        print('Exiting get_sensors_quantity() method')
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
   
    http_method_names = ['post', 'put']
 
    def put(self, request, format=None):
        flag = request.data['flag']

        if flag == protocol.STOP_EXPERIMENT_FLAG:
            utils.SerialFacade.stop_experiment()
            response = HttpResponse(status=200)
        else:
            response = HttpResponseBadRequest()
        return response

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
            utils.SerialFacade.set_frequency(frequency, start_experiment)
            status_code = 200
        except RoutineException as exception:
            status_code = exception.error_code

        return HttpResponse(status=status_code)
