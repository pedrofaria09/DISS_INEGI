# Generated by Django 2.1.7 on 2019-03-21 17:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0017_periodconfiguration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='periodconfiguration',
            name='tower',
        ),
        migrations.DeleteModel(
            name='PeriodConfiguration',
        ),
    ]
