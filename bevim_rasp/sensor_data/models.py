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

    @classmethod
    def get_sensors_quantity(cls):
        return cls.objects.count()

    def __str__(self):
        return self.name


class Data(models.Model):

    sensor = models.ForeignKey(Sensor, verbose_name='Sensor')
    x_value = models.DecimalField(max_digits=4, decimal_places=2)
    y_value = models.DecimalField(max_digits=4, decimal_places=2)
    z_value = models.DecimalField(max_digits=4, decimal_places=2)
    timestamp_ref = models.DecimalField(max_digits=17, decimal_places=2)
    job_id = models.IntegerField()

    class Meta:
        abstract = True


class Acceleration(Data):
    pass


class Frequency(Data):
    pass

