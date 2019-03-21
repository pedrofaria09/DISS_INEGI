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

# class TestConfPeriod(models.Model):
#     begin_date = models.DateField()
#     end_date = models.DateField(null=True)
#
#     def __str__(self):
#         return "%s %s" % (self.begin_date, self.end_date)
#
#
# class TestClassificationPeriod(models.Model):
#     begin_date = models.DateField()
#     end_date = models.DateField()
#     status = models.CharField(max_length=100)
#     sensorsconfiguration = models.ForeignKey('TestSensorConfig', on_delete=models.DO_NOTHING)
#
#     def __str__(self):
#         return "%s %s %s %s" % (self.begin_date, self.end_date, self.status, self.sensorsconfiguration)
#
#
# class TestDimensions(models.Model):
#     column = models.IntegerField()
#     unit = models.CharField(max_length=100)
#     sensorsconfiguration = models.ForeignKey('TestSensorConfig', on_delete=models.DO_NOTHING)
#
#     def __str__(self):
#         return "%s %s %s" % (self.column, self.unit, self.sensorsconfiguration)
#
#
# class TestSensorConfig(models.Model):
#     height = models.FloatField()
#     orientation = models.FloatField()
#     calibrations = models.ForeignKey('TestCalibration', on_delete=models.DO_NOTHING)
#     confperiods = models.ForeignKey('TestConfPeriod', on_delete=models.DO_NOTHING)
#
#     def __str__(self):
#         return "%s %s %s %s" % (self.height, self.orientation, self.calibrations, self.confperiods)
#
#
# class TestCalibration(models.Model):
#     offset = models.FloatField()
#     slope = models.FloatField(null=True)
#     equipment = models.ForeignKey('TestEquipment', on_delete=models.DO_NOTHING)
#
#     def __str__(self):
#         return "%s %s %s" % (self.offset,self.offset, self.equipment)
#
#
# class TestEquipment(models.Model):
#     sn = models.CharField(unique=True, max_length=100)
#     calibrations = models.ManyToManyField('TestCalibration', blank=True)
#
#     def __str__(self):
#         return "%s" % self.sn


class UserGroupType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return "%s" % self.name


class EquipmentType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return "%s" % self.name


class MyUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    is_client = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    group_type = models.ForeignKey('UserGroupType', on_delete=models.DO_NOTHING)
    towers = models.ManyToManyField('Tower', verbose_name="list of towers", blank=True)

    def __str__(self):
        return "%s %s" % (self.id, self.full_name)


class Station(models.Model):
    code = models.CharField(unique=True, max_length=20, null=False)
    name = models.CharField(max_length=30, null=False)

    class Meta:
        abstract = True


class Machine(Station):

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return "%s" % self.code


class Tower(Station):

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return "%s" % self.code


class Cluster(models.Model):
    name = models.CharField(unique=True, max_length=100)
    towers = models.ManyToManyField('Tower', verbose_name="list of towers", blank=True)

    def __str__(self):
        return "%s" % self.name


class Equipment(models.Model):
    sn = models.CharField(unique=True, max_length=100)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=50, null=True, blank=True)
    version = models.CharField(max_length=10, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    type = models.ForeignKey('EquipmentType', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s" % self.type


class Calibration(models.Model):
    offset = models.FloatField()
    slope = models.FloatField()
    calib_date = models.DateField(null=True, blank=True)
    ref = models.CharField(max_length=100)
    equipment = models.ForeignKey('Equipment', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "Off:%s Slop:%s Date:%s Eq:%s" % (self.offset, self.slope, self.calib_date, self.equipment)


class PeriodConfiguration(models.Model):
    begin_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    wind_rss = models.BooleanField(default=False)
    solar_rss = models.BooleanField(default=False)
    raw_freq = models.CharField(max_length=20, default="10m")
    time_zone = models.CharField(max_length=20, default="+0h")
    tower = models.ForeignKey('Tower', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s %s" % (self.begin_date, self.end_date)


class DataSetPG(models.Model):
    tower_code = models.CharField(max_length=20, null=False)
    time_stamp = models.DateTimeField(default=datetime.now, null=True, blank=True)
    value = models.CharField(max_length=200)

    class Meta:
        indexes = [
            models.Index(fields=['tower_code', 'time_stamp', ]),
            models.Index(fields=['tower_code', ]),
            models.Index(fields=['time_stamp', ])
        ]

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
