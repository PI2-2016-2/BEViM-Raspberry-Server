from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^v1/sensor$', views.SensorRestV1.as_view(), name='sensor_rest'),
    url(r'^v1/acceleration$', views.AccelerationRestV1.as_view(), name='acceleration_rest'),
    url(r'^v1/speed$', views.SpeedRestV1.as_view(), name='speed_rest'),
    url(r'^v1/amplitude$', views.AmplitudeRestV1.as_view(), name='amplitude_rest'),
    url(r'^v1/frequency$', views.FrequencyRestV1.as_view(), name='frequency_rest'),
]
