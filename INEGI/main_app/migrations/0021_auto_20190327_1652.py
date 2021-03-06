# Generated by Django 2.1.7 on 2019-03-27 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0020_auto_20190325_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentCharacteristic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manufacturer', models.CharField(blank=True, max_length=100, null=True)),
                ('model', models.CharField(blank=True, max_length=50, null=True)),
                ('version', models.CharField(blank=True, max_length=10, null=True)),
                ('designation', models.CharField(blank=True, max_length=100, null=True)),
                ('output', models.CharField(max_length=100)),
                ('gama', models.CharField(blank=True, max_length=100, null=True)),
                ('error', models.CharField(blank=True, max_length=100, null=True)),
                ('sep_field', models.CharField(blank=True, max_length=10, null=True)),
                ('sep_dec', models.CharField(blank=True, max_length=10, null=True)),
                ('sep_thousand', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='equipmenttype',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='usergrouptype',
            options={'ordering': ['-id']},
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='designation',
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='manufacturer',
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='version',
        ),
        migrations.AlterField(
            model_name='equipment',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.EquipmentCharacteristic'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.EquipmentType'),
        ),
        migrations.AddField(
            model_name='equipmentcharacteristic',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.EquipmentType'),
        ),
    ]
