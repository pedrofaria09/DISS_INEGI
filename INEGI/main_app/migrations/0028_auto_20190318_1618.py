# Generated by Django 2.1.7 on 2019-03-18 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0027_auto_20190318_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tower',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]