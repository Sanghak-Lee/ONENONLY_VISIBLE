# Generated by Django 2.2.16 on 2022-10-20 18:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20220926_1631'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verification',
            name='uuid',
        ),
        migrations.AlterField(
            model_name='verification',
            name='unique_key',
            field=models.CharField(default=django.utils.timezone.now, max_length=100, unique=True),
            preserve_default=False,
        ),
    ]