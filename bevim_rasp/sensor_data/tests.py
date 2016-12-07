from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from .models import Sensor, Acceleration, Frequency
from .serializers import AccelerationSerializer

import json

class DataRestTest(APITestCase):
    def setUp(self):
        self.sensor1 = Sensor.objects.create(name="S1")
        self.acceleration1 = Acceleration.objects.create(
            sensor=self.sensor1,
            x_value=234,
            y_value=235,
            z_value=236,
            timestamp_ref=1000,
            job_id=1
        )
        self.acceleration2 = Acceleration.objects.create(
            sensor=self.sensor1,
            x_value=100.00,
            y_value=200.00,
            z_value=300.00,
            timestamp_ref=2000.10,
            job_id=1
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

    @patch('sensor_data.utils.SerialFacade.get_available_sensors')
    def test_post_sensor(self, patch):
        # Simulating receiving another sensor from table
        sensor2 = Sensor.objects.create(name="S2")

        url = reverse('sensor_rest')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_response = [
            {
                "id": self.sensor1.pk,
                "name": self.sensor1.name
            },
            {
                "id": sensor2.pk,
                "name": sensor2.name
            }
        ]
        self.assertEqual(response.data, expected_response)

    @patch('sensor_data.utils.CurrentFrequency.get',
            return_value=(50, True))
    def test_get_current_frequency(self, patch):
        url = reverse('consult_current_frequency')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['frequency'], 50)
        self.assertEqual(response['system_status'], True)

    def test_cleaning_before_start_experiment(self):
        url = reverse('control_rest')
        response = self.client.get(url, {'experiment': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('sensor_data.utils.SerialFacade.set_frequency')
    def test_change_frequency(self, patch):
        url = reverse('control_rest')
        data = {
            'experiment': 1,
            'frequency': 60,
            'job': '1',
            'jobs_info': '{"jobs": {"1": {"frequency": 60, "job_pk": 1, "order": 1, "time": 10}}, "total_time": 10}'
        }

        # Cleaning before post
        self.client.get(url, {'experiment': 1}, format='json')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('sensor_data.utils.SerialFacade.set_frequency')
    def test_change_frequency_not_first_job(self, patch):
        url = reverse('control_rest')
        data = {
            'experiment': 1,
            'frequency': 60,
            'job': '2',
            'jobs_info': '{"jobs": {"1": {"frequency": 60, "job_pk": 1, "order": 1, "time": 10}, "2": {"frequency": 60, "job_pk": 2, "order": 2, "time": 10}}, "total_time": 20}'
        }

        # Cleaning before post
        self.client.get(url, {'experiment': 1}, format='json')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('sensor_data.views.ActiveExperiment.check', return_value=False)
    @patch('sensor_data.views.ActiveExperiment.remove')
    @patch('sensor_data.utils.SerialFacade.stop_experiment')
    def test_stop_experiment(self, patch, patch2, patch3):
        url = reverse('control_rest')
        data = {'experiment': 1, 'forced_stop': False}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('sensor_data.views.ActiveExperiment.check', return_value=False)
    def test_stop_experiment(self, patch):
        url = reverse('control_rest')
        data = {'experiment': 1, 'forced_stop': False}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)