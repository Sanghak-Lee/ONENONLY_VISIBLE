# Generated by Django 2.2.16 on 2022-10-04 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20220927_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswer',
            name='job',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]