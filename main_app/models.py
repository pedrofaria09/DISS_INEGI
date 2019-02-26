from django.db import models
from mongoengine import *
from django.contrib.auth.models import AbstractUser
from influxdb import InfluxDBClient, SeriesHelper

import datetime

# Connection to MongoDB
connect('INEGI')

# Connection to InfluxDB
myclient = InfluxDBClient(host='localhost', port=8086, database='INEGI_INFLUX')

# Create your models here.


class MyUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True)
    is_client = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)


class Tower(models.Model):
    code = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=30, null=False)


class DataRaw(EmbeddedDocument):
    time = DateTimeField(default=datetime.datetime.utcnow)
    data = StringField(max_length=200)


class TowerData(Document):
    tower_code = StringField(max_length=20)
    raw_datas = ListField(EmbeddedDocumentField(DataRaw))


class InfluxData(models.Model):
    time = models.DateTimeField(db_column="time", primary_key=True)
    value = models.CharField(max_length=100, null=False, db_column="value")


class Meta:
    managed = False
    db_table = 'test'


class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = myclient

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = '{measurement}'

        # Defines all the fields in this time series.
        fields = ['value', 'time']

        # Defines all the tags for the series.
        tags = ['measurement']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5

        # autocommit must be set to True when using bulk_size
        autocommit = True

