# Generated by Django 2.1.2 on 2018-10-28 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivalpickr', '0006_auto_20181027_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='band',
            name='name',
            field=models.CharField(db_index=True, max_length=300, unique=True),
        ),
        migrations.AlterField(
            model_name='festival',
            name='name',
            field=models.CharField(db_index=True, max_length=100, unique=True),
        ),
    ]