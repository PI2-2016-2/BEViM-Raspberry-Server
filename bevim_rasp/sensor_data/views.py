from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Acceleration, Sensor, Speed, Amplitude, Frequency
from .serializers import SensorSerializer, DataSerializer
from rest_framework import status


class SensorRestV1(APIView):

    EXPERIMENT_START_FREQUENCY = '-2'

    def get(self, request, format=None):
        sensors = Sensor.objects.all()
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):    

        data = request.data
        if data and (data['value'] == self.EXPERIMENT_START_FREQUENCY):
            serializer = self.get_sensors_quantity()
            response = Response(serializer.data)
        else:
            response = Response(data)

        return response

    def get_sensors_quantity(self):
        # Test
        data = {
            'name': 'S1'
        }
        serializer = SensorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print (serializer.errors)

        return serializer

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