# Generated by Django 2.2.16 on 2022-12-16 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_verification_last_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verification',
            name='last_verified',
            field=models.DateTimeField(auto_now_add=True, help_text='마지막 인증날짜'),
        ),
    ]