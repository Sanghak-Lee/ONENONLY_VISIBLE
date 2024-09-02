# Generated by Django 2.2.16 on 2022-12-09 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0021_auto_20221205_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placement',
            name='placement_type',
            field=models.CharField(choices=[('crowdfunding', '일반구매'), ('secretfunding', '경쟁구매'), ('openfunding', '경매')], default='openfunding', help_text='경매 종류', max_length=20),
        ),
    ]
