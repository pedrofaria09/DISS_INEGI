# Generated by Django 2.1.7 on 2019-04-23 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0055_auto_20190418_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipmenttype',
            name='initials',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
