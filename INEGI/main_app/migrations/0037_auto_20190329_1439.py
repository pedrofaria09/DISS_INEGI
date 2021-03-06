# Generated by Django 2.1.7 on 2019-03-29 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0036_auto_20190328_2040'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCalibration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offset', models.FloatField()),
                ('slope', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestConfPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_date', models.DateField()),
                ('end_date', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestEquipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn', models.CharField(max_length=100, unique=True)),
                ('calibrations', models.ManyToManyField(blank=True, to='main_app.TestCalibration')),
            ],
        ),
        migrations.CreateModel(
            name='TestSensorConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.FloatField()),
                ('orientation', models.FloatField()),
                ('calibrations', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.TestCalibration')),
                ('confperiods', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.TestConfPeriod')),
            ],
        ),
        migrations.AddField(
            model_name='testcalibration',
            name='equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.TestEquipment'),
        ),
    ]
