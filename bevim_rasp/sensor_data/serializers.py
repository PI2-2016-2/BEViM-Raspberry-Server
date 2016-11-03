from rest_framework import serializers
from .models import Sensor, Acceleration, Frequency


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'


class AccelerationSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer()

    class Meta:
        model = Acceleration
        fields = '__all__'


class FrequencySerializer(serializers.ModelSerializer):
    sensor = SensorSerializer()

    class Meta:
        model = Frequency
        fields = '__all__'

