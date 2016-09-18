from django.db import models
from django.core import validators


class Sensor(models.Model):
    name = models.CharField(
        "Sensor name",
        max_length=3,
        validators=[
            validators.RegexValidator(
                r'^[a-zA-Z0-9_\s+]+$',
                'Use alphanumeric characters and underscore only'
            )
        ],
        blank=False
    )

    def __str__(self):
        return self.name


class Data(models.Model):
    sensor = models.ForeignKey(Sensor, verbose_name='Sensor')
    value = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


class Acceleration(Data):
    pass


class Speed(Data):
    pass


class Amplitude(Data):
    pass


class Frequency(Data):
    pass
