# Generated by Django 2.1.7 on 2019-03-11 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_auto_20190311_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetpg',
            name='tower_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main_app.Tower'),
        ),
    ]
