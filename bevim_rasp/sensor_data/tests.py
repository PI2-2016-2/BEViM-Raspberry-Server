from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Sensor, Acceleration, Speed, Amplitude, Frequency
from .serializers import DataSerializer


class DataRestTest(APITestCase):
    def setUp(self):
        self.sensor1 = Sensor.objects.create(name="S1")
        self.acceleration1 = Acceleration.objects.create(
            sensor=self.sensor1, value=234
        )
        self.acceleration2 = Acceleration.objects.create(
            sensor=self.sensor1, value=987
        )
        self.speed = Speed.objects.create(sensor=self.sensor1, value=432)
        self.amplitude = Amplitude.objects.create(
            sensor=self.sensor1, value=123
        )
        self.frequency = Frequency.objects.create(
            sensor=self.sensor1, value=20
        )

    def test_get_sensor(self):
        url = reverse('sensor_rest')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response = [{
            "id": self.sensor1.pk,
            "name": self.sensor1.name
        }]
        self.assertEqual(response.data, expected_response)

    def test_get_acceleration(self):
        url = reverse('acceleration_rest')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        accelerations = Acceleration.objects.all()
        expected_response = DataSerializer(accelerations, many=True).data
        self.assertEqual(response.data, expected_response)


    def test_get_frequency(self):
        url = reverse('frequency_rest')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        frequencies = Frequency.objects.all()
        expected_response = DataSerializer(frequencies, many=True).data
        self.assertEqual(response.data, expected_response)
