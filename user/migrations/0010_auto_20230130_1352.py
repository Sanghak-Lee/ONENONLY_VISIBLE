# Generated by Django 2.2.16 on 2023-01-30 13:52

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20221216_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='avatar',
            field=models.ImageField(blank=True, help_text='50x50 사이즈 작은 프로필이미지', upload_to=user.models.custom_avatar_path),
        ),
    ]
