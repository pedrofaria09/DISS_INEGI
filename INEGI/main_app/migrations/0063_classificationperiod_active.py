# Generated by Django 2.1.7 on 2019-04-24 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0062_auto_20190424_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='classificationperiod',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
