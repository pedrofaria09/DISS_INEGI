# Generated by Django 2.1.7 on 2019-04-15 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0043_componenttype_metrictype_statistictype_unittype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dimension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DimensionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.ComponentType')),
                ('metric', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.MetricType')),
                ('statistic', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.StatisticType')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.UnitType')),
            ],
        ),
        migrations.AddField(
            model_name='dimension',
            name='dimension_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.DimensionType'),
        ),
        migrations.AddField(
            model_name='dimension',
            name='equipment_configuration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.EquipmentConfig'),
        ),
        migrations.AlterUniqueTogether(
            name='dimensiontype',
            unique_together={('unit', 'statistic', 'metric', 'component')},
        ),
    ]
