# Generated by Django 2.2.16 on 2022-09-14 11:31

import auction.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0007_auto_20220914_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='placementmemory',
            name='history_background',
            field=models.ImageField(help_text='Remember Background', null=True, upload_to=auction.models.custom_remember_image_path),
        ),
    ]
