from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Acceleration, Sensor, Frequency
from . import utils, protocol
from .serializers import SensorSerializer, AccelerationSerializer, FrequencySerializer
from .exceptions import RoutineException

import json, time, datetime


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
        serializer = AccelerationSerializer(accelerations, many=True)
        return Response(serializer.data)


class FrequencyRestV1(APIView):

    def get(self, request, format=None):
        frequencies = Frequency.objects.all()
        serializer = FrequencySerializer(frequencies, many=True)
        return Response(serializer.data)

    @classmethod
    def get_current_frequency(cls, request):
        current_frequency = utils.CurrentFrequency.get_instance().get()
        now = str(datetime.datetime.now().time())
        return HttpResponse(json.dumps({'timestamp': now, 'frequency': current_frequency}))

class ControlRestV1(APIView):

    http_method_names = ['post', 'put']
    start_time = 0
    end_time = 0

    def put(self, request, format=None):

        flag = request.data['flag']

        if flag == protocol.STOP_EXPERIMENT_FLAG:
            #utils.SerialFacade.stop_experiment() # UNCOMMENT THIS - JUST FOR TEST WHILE THE SIMULATION IS NOT RIGHT
            # Clean the Current Frequency when experiment is over
            utils.CurrentFrequency.clean()
            response = HttpResponse(status=200)
        else:
            response = HttpResponseBadRequest()
        return response

    def post(self, request, format=None):
        print("ON CHANGE FREQUENCY POST")
        self.start_time = datetime.datetime.now().time()
        print(self.start_time)
        time.sleep(3)
        """
        This method is used to change the frequency of the table
        """
        job = request.data['job']
        jobs = request.data['jobs_info']
        jobs_info = json.loads(jobs)
        print(jobs_info)
        print("Change frequency service called for Job Nº" + job)
        frequency = request.data['frequency']
        try:
            start_experiment = False
            if job is '1':
                # If is the first job, set the start experiment flag to true
                start_experiment = True

            utils.SerialFacade.set_frequency(frequency, start_experiment, jobs_info)

            ########################### - USED TO SIMULATE THE TABLE FREQUENCY RAISE
            # utils.CurrentFrequency.get_instance().update(80);
            ###########################

            status_code = 200
        except RoutineException as exception:
            status_code = exception.error_code

        return HttpResponse(status=status_code)
