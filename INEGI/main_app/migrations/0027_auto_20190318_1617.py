# Generated by Django 2.1.7 on 2019-03-18 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0026_auto_20190318_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tower',
            name='name',
            field=models.CharField(default=models.CharField(max_length=20, primary_key=True, serialize=False), max_length=30, null=True),
        ),
    ]
