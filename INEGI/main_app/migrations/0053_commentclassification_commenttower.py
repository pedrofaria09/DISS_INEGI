# Generated by Django 2.1.7 on 2019-04-16 13:56

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0052_auto_20190416_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('internal_comment', models.TextField(blank=True, null=True)),
                ('compact_comment', models.TextField(blank=True, null=True)),
                ('detailed_comment', models.TextField(blank=True, null=True)),
                ('begin_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('classification', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.ClassificationPeriod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentTower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('internal_comment', models.TextField(blank=True, null=True)),
                ('compact_comment', models.TextField(blank=True, null=True)),
                ('detailed_comment', models.TextField(blank=True, null=True)),
                ('begin_date', models.DateTimeField(default=datetime.datetime.now)),
                ('end_date', models.DateTimeField(default=datetime.datetime.now)),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.Tower')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
