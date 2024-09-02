# Generated by Django 2.2.16 on 2023-05-21 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20230407_2242'),
    ]

    operations = [
        migrations.RenameField(
            model_name='articles',
            old_name='short_text',
            new_name='display_text',
        ),
        migrations.AddField(
            model_name='articles',
            name='display_day',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='articles',
            name='display_place',
            field=models.TextField(blank=True, null=True),
        ),
    ]
