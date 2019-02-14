# Generated by Django 2.1.5 on 2019-02-11 11:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='arrival_time_sharer',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='ride',
            name='destination_sharer',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='ride',
            name='passengers_sharer',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='ride',
            name='sharer_email',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='ride',
            name='sharer_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='ride',
            name='sharer_phone',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
