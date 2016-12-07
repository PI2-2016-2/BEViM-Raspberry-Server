from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^sensor$', views.SensorRestV1.as_view(), name='sensor_rest'),
    #  Control URLS
    url(r'^control/change_frequency$', views.ControlRestV1.as_view(), name='control_rest'),
    url(r'^consult/current_frequency$', views.FrequencyRestV1.as_view(), name='consult_current_frequency'),
]
