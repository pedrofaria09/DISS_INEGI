from django.db import models
from mongoengine import *
import datetime

connect('INEGI')

# Create your models here.

class Tower(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=30)


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

