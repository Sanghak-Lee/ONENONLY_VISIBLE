# Generated by Django 2.2.16 on 2023-01-27 17:53

import core.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20230119_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articles',
            name='thumbnail',
            field=models.ImageField(default=django.utils.timezone.now, upload_to=core.models.custom_article_path),
            preserve_default=False,
        ),
    ]
