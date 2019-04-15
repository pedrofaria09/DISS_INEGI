from django.db import models
from mongoengine import *
from django.contrib.auth.models import AbstractUser
from influxdb import InfluxDBClient, SeriesHelper
from datetime import datetime
from django.conf import settings
from django.db.models import Q as QD

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
class TestConfPeriod(models.Model):
    begin_date = models.DateField()
    end_date = models.DateField(null=True)

    def __str__(self):
        return "%s %s" % (self.begin_date, self.end_date)


class TestSensorConfig(models.Model):
    height = models.FloatField()
    orientation = models.FloatField()
    calibrations = models.ForeignKey('TestCalibration', on_delete=models.DO_NOTHING)
    confperiods = models.ForeignKey('TestConfPeriod', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s %s %s %s" % (self.height, self.orientation, self.calibrations, self.confperiods)


class TestCalibration(models.Model):
    offset = models.FloatField()
    slope = models.FloatField(null=True)
    equipment = models.ForeignKey('TestEquipment', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s %s %s" % (self.offset,self.offset, self.equipment)


class TestEquipment(models.Model):
    sn = models.CharField(unique=True, max_length=100)
    calibrations = models.ManyToManyField('TestCalibration', blank=True)

    def __str__(self):
        return "%s" % self.sn

#
# class TestTower(models.Model):
#     name = models.CharField(max_length=128)
#
#     def __str__(self):
#         return self.name
#
#
# class TestUser(models.Model):
#     name = models.CharField(max_length=128)
#     members = models.ManyToManyField('TestDates', blank=True)
#
#     def __str__(self):
#         return self.name
#
#
# class TestDates(models.Model):
#     tower = models.ManyToManyField('TestTower', blank=True)
#     user = models.ForeignKey('TestUser', on_delete=models.CASCADE)
#     begin_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#
#     def __str__(self):
#         return "Tower:%s User:%s" % (self.tower.name, self.user)


class UserGroupType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class EquipmentType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class UnitType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class StatisticType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class MetricType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class ComponentType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class UserTowerDates(models.Model):
    tower = models.ManyToManyField('Tower', blank=True)
    user = models.ForeignKey('MyUser', on_delete=models.DO_NOTHING)
    begin_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return "Tower:%s User:%s" % (self.tower.all, self.user)


class MyUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    is_client = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    group_type = models.ForeignKey('UserGroupType', on_delete=models.DO_NOTHING)
    towers = models.ManyToManyField('UserTowerDates', blank=True)

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


class PeriodConfiguration(models.Model):
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    wind_rss = models.BooleanField(default=False)
    solar_rss = models.BooleanField(default=False)
    raw_freq = models.CharField(max_length=20, default="10m")
    time_zone = models.CharField(max_length=20, default="+0h")
    tower = models.ForeignKey('Tower', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s %s" % (self.begin_date, self.end_date)


class EquipmentConfig(models.Model):
    height = models.FloatField()
    height_label = models.CharField(max_length=20, null=True, blank=True)
    orientation = models.FloatField(null=True, blank=True)
    boom_length = models.FloatField(null=True, blank=True)
    boom_var_height = models.FloatField(null=True, blank=True)
    calibration = models.ForeignKey('Calibration', on_delete=models.DO_NOTHING)
    conf_period = models.ForeignKey('PeriodConfiguration', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s %s %s %s" % (self.height, self.calibration.slope, self.conf_period.begin_date, self.conf_period.end_date)


class Equipment(models.Model):
    sn = models.CharField(unique=True, max_length=100)
    model = models.ForeignKey('EquipmentCharacteristic', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s" % self.sn


class EquipmentCharacteristic(models.Model):
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=50, null=True, blank=True)
    version = models.CharField(max_length=10, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    output = models.CharField(max_length=100)
    gama = models.CharField(max_length=100, null=True, blank=True)
    error = models.CharField(max_length=100, null=True, blank=True)
    sep_field = models.CharField(max_length=10, null=True, blank=True)
    sep_dec = models.CharField(max_length=10, null=True, blank=True)
    sep_thousand = models.CharField(max_length=10, null=True, blank=True)
    type = models.ForeignKey('EquipmentType', on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s - %s - %s" % (self.type, self.model, self.version)


class Calibration(models.Model):
    offset = models.FloatField()
    slope = models.FloatField()
    calib_date = models.DateTimeField(null=True, blank=True)
    ref = models.CharField(max_length=100)
    equipment = models.ForeignKey('Equipment', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "SN:%s Ref:%s OF:%s SL:%s" % (self.equipment, self.ref, self.offset, self.slope)


class Status(models.Model):
    code = models.FloatField(unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = (("code", "name"),)

    def __str__(self):
        return "%s %s" % (self.code, self.name)


class ClassificationPeriod(models.Model):
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField()
    equipment_configuration = models.ForeignKey('EquipmentConfig', on_delete=models.DO_NOTHING)
    status = models.ForeignKey('Status', on_delete=models.DO_NOTHING)
    user = models.ForeignKey('MyUser', on_delete=models.DO_NOTHING)


class Dimension(models.Model):
    column = models.IntegerField()
    dimension_type = models.ForeignKey('DimensionType', on_delete=models.DO_NOTHING)
    equipment_configuration = models.ForeignKey('EquipmentConfig', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s %s" % (self.column, self.dimension_type)


class DimensionType(models.Model):
    unit = models.ForeignKey('UnitType', on_delete=models.DO_NOTHING)
    statistic = models.ForeignKey('StatisticType', on_delete=models.DO_NOTHING)
    metric = models.ForeignKey('MetricType', on_delete=models.DO_NOTHING)
    component = models.ForeignKey('ComponentType', on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta:
        unique_together = (("unit", "statistic", "metric", "component"),)

    def __str__(self):
        return "%s %s %s %s" % (self.unit, self.statistic, self.metric, self.component)


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
