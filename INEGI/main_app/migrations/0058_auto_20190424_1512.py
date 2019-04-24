# Generated by Django 2.1.7 on 2019-04-24 15:12

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0057_auto_20190423_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='country',
            field=django_countries.fields.CountryField(default='PT', max_length=2),
        ),
        migrations.AddField(
            model_name='tower',
            name='country',
            field=django_countries.fields.CountryField(default='PT', max_length=2),
        ),
    ]
