# Generated by Django 2.1.7 on 2019-03-18 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0023_auto_20190318_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='towers',
            field=models.ManyToManyField(blank=True, to='main_app.Tower', verbose_name='list of towers'),
        ),
    ]