# Generated by Django 2.1.2 on 2018-10-27 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivalpickr', '0004_auto_20181027_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='songkickid',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]