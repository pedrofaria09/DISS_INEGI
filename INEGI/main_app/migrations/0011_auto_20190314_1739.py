# Generated by Django 2.1.7 on 2019-03-14 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0010_cluster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='towers',
            field=models.ManyToManyField(to='main_app.Tower', verbose_name='list of towers'),
        ),
    ]
