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
        current_frequency, system_status = utils.CurrentFrequency.get_instance().get()
        now = str(datetime.datetime.now().time())
        return HttpResponse(json.dumps({
            'timestamp': now,
            'frequency': current_frequency,
            'system_status': system_status
        }))

class ControlRestV1(APIView):

    http_method_names = ['get', 'post', 'put']

    def get(self, request, format=None):
        """ Do here stuff before the experiment start
        """
        print("New experiment starting...")
        experiment_id = request.GET['experiment']
        # Cleaning variables to start new experiment
        ActiveExperiment.clean()
        utils.CurrentFrequency.clean()
        return HttpResponse(status=200)

    def put(self, request, format=None):

        experiment_id = request.data['experiment']
        forced_stop = request.data['forced_stop']

        if ActiveExperiment.get_instance().check(experiment_id):
            # Sending signal to stop collecting data

            # utils.SerialFacade.stop_experiment() # UNCOMMENT THIS - JUST FOR TEST WHILE THE SIMULATION IS NOT RIGHT

            # Clean the Current Frequency instance when experiment is over
            utils.CurrentFrequency.clean()

            # Removing experiment from active ones
            ActiveExperiment.get_instance().remove(experiment_id)
            response = HttpResponse(status=200)
        else:
            response = HttpResponseBadRequest("This experiment no longer active.")
        return response


    def post(self, request, format=None):
        """
        This method is used to change the frequency of the table
        """
        experiment = request.data['experiment']
        job = request.data['job']
        jobs = request.data['jobs_info']
        jobs_info = json.loads(jobs)
        frequency = request.data['frequency']

        print("Change frequency service called for Job Nº %s" % job)

        status_code = 200
        if ActiveExperiment.get_instance().get(experiment):
            try:
                start_experiment = False
                if job is '1':
                    # If is the first job, set the start experiment flag to true
                    start_experiment = True

                ########################### - COMMENTED TO SIMULATE THE TABLE FREQUENCY RAISE
                utils.SerialFacade.set_frequency(frequency, start_experiment, jobs_info)
                ########################### - USED TO SIMULATE THE TABLE FREQUENCY RAISE

                ########################### - USED TO SIMULATE THE TABLE FREQUENCY RAISE
                # utils.CurrentFrequency.get_instance().update(20);
                ###########################

            except RoutineException as exception:
                status_code = exception.error_code

        return HttpResponse(status=status_code)

class ActiveExperiment:

    instance = None;

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = ActiveExperiment()
        return cls.instance

    def __init__(self):
        self.experiments = []

    def check(self, experiment_id):
        return experiment_id in self.experiments

    def get(self, experiment_id):
        if self.check(experiment_id):
            return False
        else:
            self.experiments.append(experiment_id)
            return True

    def remove(self, experiment_id):
        if self.check(experiment_id):
            self.experiments.remove(experiment_id)

    @classmethod
    def clean(cls):
        cls.instance = None
