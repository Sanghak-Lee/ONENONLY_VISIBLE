# Generated by Django 2.2.16 on 2023-03-05 12:55

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20230220_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='articles',
            name='badge',
            field=models.ImageField(default='default.png', help_text='섬네일 옆 배지 이미지', upload_to=core.models.custom_article_path),
        ),
    ]
