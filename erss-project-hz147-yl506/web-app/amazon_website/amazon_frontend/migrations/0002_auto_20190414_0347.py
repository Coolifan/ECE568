# Generated by Django 2.2 on 2019-04-14 03:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amazon_frontend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='warehouse',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='amazon_frontend.Warehouse'),
        ),
    ]
