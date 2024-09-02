# Generated by Django 2.2.16 on 2022-10-18 21:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_questionanswer_job'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupon',
            options={'ordering': ['updated'], 'verbose_name': '쿠폰', 'verbose_name_plural': '쿠폰들'},
        ),
        migrations.AddField(
            model_name='coupon',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coupon',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
