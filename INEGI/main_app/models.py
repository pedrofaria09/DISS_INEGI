from django.db import models
from mongoengine import *
from django.contrib.auth.models import AbstractUser
from influxdb import InfluxDBClient, SeriesHelper
from datetime import datetime
from django.conf import settings
from django_countries.fields import CountryField
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


class AffiliationType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class UserGroupType(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "%s" % self.name


class EquipmentType(models.Model):
    name = models.CharField(unique=True, max_length=100)
    initials = models.CharField(unique=True, max_length=50)

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
    group_type = models.ForeignKey('UserGroupType', on_delete=models.DO_NOTHING, null=True, blank=True)
    towers = models.ManyToManyField('UserTowerDates', blank=True)
    affiliation = models.ForeignKey('AffiliationType', on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.id, self.full_name)


class Station(models.Model):
    code_inegi = models.CharField(unique=True, max_length=20)
    code_aux_1 = models.CharField(max_length=20, blank=True, null=True)
    code_aux_2 = models.CharField(max_length=20, blank=True, null=True)
    code_client = models.CharField(max_length=20, blank=True, null=True)
    designation = models.CharField(max_length=30, blank=True, null=True)
    position_x = models.FloatField(default="0")
    position_y = models.FloatField(default="0")
    utm_zone = models.CharField(max_length=20, blank=True, null=True)
    coords_system = models.CharField(max_length=20, default="0")
    installation_date = models.DateTimeField(null=True, blank=True)
    project = models.CharField(max_length=30, null=True, blank=True)
    client = models.ForeignKey('AffiliationType', on_delete=models.DO_NOTHING, null=True, blank=True)
    parish = models.CharField(max_length=30, null=True, blank=True)
    district = models.CharField(max_length=30, null=True, blank=True)
    country = CountryField(default="PT")
    gsm_number = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class Machine(Station):

    class Meta:
        ordering = ["code_inegi"]

    def __str__(self):
        return "%s" % self.code_inegi


class Tower(Station):

    class Meta:
        ordering = ["code_inegi"]

    def __str__(self):
        return "%s" % self.code_inegi


class Cluster(models.Model):
    name = models.CharField(unique=True, max_length=100)
    towers = models.ManyToManyField('Tower', verbose_name="list of towers", blank=True)

    def __str__(self):
        return "%s" % self.name


class PeriodConfiguration(models.Model):
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
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
        return "%s @ %s" % (self.calibration.equipment.model.type.name, self.height)


class Equipment(models.Model):
    sn = models.CharField(unique=True, max_length=100)
    model = models.ForeignKey('EquipmentCharacteristic', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s - %s" % (self.sn, self.model.type.name)


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
    dimension_type = models.ForeignKey('DimensionType', on_delete=models.DO_NOTHING)

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


class Comment(models.Model):
    comment_date = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey('MyUser', on_delete=models.DO_NOTHING)
    internal_comment = models.TextField(null=True, blank=True)
    compact_comment = models.TextField(null=True, blank=True)
    detailed_comment = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class CommentTower(Comment):
    begin_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default=datetime.now)
    tower = models.ForeignKey('Tower', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s" % self.tower


class CommentClassification(Comment):
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField()
    classification = models.ForeignKey('ClassificationPeriod', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "%s" % self.classification.equipment_configuration.calibration.sn


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
