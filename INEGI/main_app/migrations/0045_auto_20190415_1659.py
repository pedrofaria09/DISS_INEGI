# Generated by Django 2.1.7 on 2019-04-15 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0044_auto_20190415_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dimensiontype',
            name='component',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.ComponentType'),
        ),
    ]