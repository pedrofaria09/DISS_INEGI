# Generated by Django 2.1.7 on 2019-04-25 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0067_calibration_dimension_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calibration',
            name='dimension_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.DimensionType'),
        ),
    ]
