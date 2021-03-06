# Generated by Django 2.1.7 on 2019-04-24 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0058_auto_20190424_1512'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='machine',
            options={'ordering': ['code_inegi']},
        ),
        migrations.AlterModelOptions(
            name='tower',
            options={'ordering': ['code_inegi']},
        ),
        migrations.RenameField(
            model_name='machine',
            old_name='code',
            new_name='code_inegi',
        ),
        migrations.RenameField(
            model_name='machine',
            old_name='name',
            new_name='designation',
        ),
        migrations.RenameField(
            model_name='tower',
            old_name='code',
            new_name='code_inegi',
        ),
        migrations.RenameField(
            model_name='tower',
            old_name='name',
            new_name='designation',
        ),
    ]
