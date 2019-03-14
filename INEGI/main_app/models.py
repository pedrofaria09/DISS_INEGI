from django.db import models
from mongoengine import *
from django.contrib.auth.models import AbstractUser
from influxdb import InfluxDBClient, SeriesHelper
from datetime import datetime
from django.conf import settings

# Connection to MongoDB
if settings.DOCKER:
    connect(db='INEGI', host='mongo')
else:
    connect(db='INEGI', host='localhost')

# Connection test for mongo in the server
# connect(host="mongodb+srv://pedro:pedrofaria@cluster0-rparn.mongodb.net/test?retryWrites=true")

# Connection to InfluxDB
if settings.DOCKER:
    INFLUXCLIENT = InfluxDBClient(host='influx', port=8086, database='INEGI_INFLUX')
else:
    INFLUXCLIENT = InfluxDBClient(host='localhost', port=8086, database='INEGI_INFLUX')

# Create your models here.

class MyUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True)
    is_client = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s" % (self.id, self.full_name)


class Tower(models.Model):
    code = models.CharField(primary_key=True, max_length=20, null=False)
    name = models.CharField(max_length=30, null=False)

    def __str__(self):
        return "%s" % self.code


class DataSetPG(models.Model):
    # tower_code = models.ForeignKey(Tower, on_delete=models.SET_NULL, blank=True, null=True) # Cant use, because we can have datasets without towers
    tower_code = models.CharField(db_index=True, max_length=20, null=False)
    time_stamp = models.DateTimeField(db_index=True, default=datetime.now, null=True, blank=True)
    value = models.CharField(max_length=200)

    def __str__(self):
        return "%s" % self.tower_code


class DataSetMongo(DynamicDocument):
    tower_code = StringField(max_length=20)
    time_stamp = DateTimeField(default=datetime.now)
    value = StringField(max_length=200)
    meta = {"indexes": ['tower_code', 'time_stamp']}

    def __str__(self):
        return "%s" % self.tower_code


class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = INFLUXCLIENT

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = '{measurement}'

        # Defines all the fields in this time series.
        fields = ['value', 'time']

        # Defines all the tags for the series.
        tags = ['measurement']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 2000

        # autocommit must be set to True when using bulk_size
        autocommit = True

