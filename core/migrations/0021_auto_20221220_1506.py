# Generated by Django 2.2.16 on 2022-12-20 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_coupon_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elasticinfo',
            name='tag',
            field=models.CharField(help_text='식별가능한 문자열', max_length=20, primary_key=True, serialize=False),
        ),
    ]
