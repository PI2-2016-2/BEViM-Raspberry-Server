from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Acceleration, Sensor, Speed, Amplitude, Frequency
from .serializers import SensorSerializer, DataSerializer


class SensorRestV1(APIView):

    def get(self, request, format=None):
        sensors = Sensor.objects.all()
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)


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
