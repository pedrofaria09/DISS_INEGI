# Generated by Django 2.1.7 on 2019-04-24 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0063_classificationperiod_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classificationperiod',
            name='active',
        ),
        migrations.AddField(
            model_name='periodconfiguration',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
