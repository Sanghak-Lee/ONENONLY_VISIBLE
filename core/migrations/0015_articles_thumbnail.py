# Generated by Django 2.2.16 on 2022-11-16 11:49

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20221018_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='articles',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.custom_article_path),
        ),
    ]
