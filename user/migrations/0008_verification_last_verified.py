# Generated by Django 2.2.16 on 2022-12-15 12:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20221020_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='verification',
            name='last_verified',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
