# Generated by Django 2.2 on 2019-04-20 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon_frontend', '0004_auto_20190419_0244'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]