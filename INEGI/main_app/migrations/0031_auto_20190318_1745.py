# Generated by Django 2.1.7 on 2019-03-18 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0030_auto_20190318_1743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipment',
            name='id',
        ),
        migrations.AlterField(
            model_name='equipment',
            name='manufacturer',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='sn',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]