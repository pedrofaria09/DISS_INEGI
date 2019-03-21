# Generated by Django 2.1.7 on 2019-03-21 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0016_auto_20190321_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('wind_rss', models.BooleanField(default=False)),
                ('solar_rss', models.BooleanField(default=False)),
                ('raw_freq', models.CharField(default='10m', max_length=20)),
                ('time_zone', models.CharField(default='+0h', max_length=20)),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.Tower')),
            ],
        ),
    ]
