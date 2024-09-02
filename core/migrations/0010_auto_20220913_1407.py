# Generated by Django 2.2.16 on 2022-09-13 14:07

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_partnership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elasticinfo',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.custom_info_path),
        ),
        migrations.AlterField(
            model_name='elasticinfo',
            name='info',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='elasticinfo',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to=core.models.custom_info_path),
        ),
    ]
