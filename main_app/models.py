from django.db import models
from mongoengine import *
from django.contrib.auth.models import AbstractUser

import datetime

connect('INEGI')

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

