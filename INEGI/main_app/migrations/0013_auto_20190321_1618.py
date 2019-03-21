# Generated by Django 2.1.7 on 2019-03-21 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0012_testcalibration_slope'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testcalibration',
            name='equipment',
        ),
        migrations.RemoveField(
            model_name='testclassificationperiod',
            name='sensorsconfiguration',
        ),
        migrations.RemoveField(
            model_name='testdimensions',
            name='sensorsconfiguration',
        ),
        migrations.RemoveField(
            model_name='testequipment',
            name='calibrations',
        ),
        migrations.RemoveField(
            model_name='testsensorconfig',
            name='calibrations',
        ),
        migrations.RemoveField(
            model_name='testsensorconfig',
            name='confperiods',
        ),
        migrations.DeleteModel(
            name='TestCalibration',
        ),
        migrations.DeleteModel(
            name='TestClassificationPeriod',
        ),
        migrations.DeleteModel(
            name='TestConfPeriod',
        ),
        migrations.DeleteModel(
            name='TestDimensions',
        ),
        migrations.DeleteModel(
            name='TestEquipment',
        ),
        migrations.DeleteModel(
            name='TestSensorConfig',
        ),
    ]
