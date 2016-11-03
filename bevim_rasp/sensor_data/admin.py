from django.contrib import admin
from . import models

admin.site.register(models.Sensor)
admin.site.register(models.Acceleration)
admin.site.register(models.Frequency)

