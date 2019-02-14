# Generated by Django 2.1.5 on 2019-02-11 07:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(max_length=200)),
                ('owner_email', models.CharField(max_length=200)),
                ('owner_phone', models.CharField(max_length=200)),
                ('owner_id', models.IntegerField()),
                ('destination_owner', models.CharField(max_length=200)),
                ('arrival_time_owner', models.DateTimeField(default=datetime.datetime.now)),
                ('passengers_owner', models.IntegerField(default=1)),
                ('is_shareable', models.BooleanField(default=True)),
                ('vehicle_type_requested', models.CharField(blank=True, max_length=200)),
                ('special_requests_owner', models.CharField(blank=True, max_length=200)),
                ('driver_name', models.CharField(max_length=200)),
                ('driver_email', models.CharField(max_length=200)),
                ('driver_phone', models.CharField(max_length=200)),
                ('driver_id', models.IntegerField(blank=True)),
                ('vehicle_type_registered', models.CharField(max_length=200)),
                ('license_plate_number', models.CharField(max_length=200)),
                ('max_capacity', models.IntegerField(default=4)),
                ('special_requests_driver', models.CharField(max_length=200)),
                ('sharer_name', models.CharField(max_length=200)),
                ('sharer_email', models.CharField(max_length=200)),
                ('sharer_phone', models.CharField(max_length=200)),
                ('sharer_id', models.IntegerField(blank=True)),
                ('destination_sharer', models.CharField(max_length=200)),
                ('arrival_time_sharer', models.DateTimeField(default=datetime.datetime.now)),
                ('passengers_sharer', models.IntegerField(default=1)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('is_completed', models.BooleanField(default=False)),
            ],
        ),
    ]