# Generated by Django 2.1.5 on 2019-02-11 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=200)),
                ('vehicle_type_registered', models.CharField(max_length=200)),
                ('license_plate_number', models.CharField(max_length=200)),
                ('max_capacity', models.IntegerField(default=4)),
                ('special_requests', models.CharField(max_length=200)),
            ],
        ),
    ]
