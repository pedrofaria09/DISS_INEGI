# Generated by Django 2.1.7 on 2019-04-09 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0039_status'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='status',
            unique_together={('code', 'name')},
        ),
    ]
