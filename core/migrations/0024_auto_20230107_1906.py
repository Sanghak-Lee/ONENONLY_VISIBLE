# Generated by Django 2.2.16 on 2023-01-07 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20230106_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='receipt_url',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
