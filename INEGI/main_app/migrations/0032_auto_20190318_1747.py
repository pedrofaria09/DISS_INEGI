# Generated by Django 2.1.7 on 2019-03-18 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0031_auto_20190318_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='manufacturer',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
