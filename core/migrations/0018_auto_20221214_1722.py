# Generated by Django 2.2.16 on 2022-12-14 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20221209_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='crowdfundingorderitem',
            name='ticket_checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='openfundingorderitem',
            name='ticket_checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='secretfundingorderitem',
            name='ticket_checked',
            field=models.BooleanField(default=False),
        ),
    ]
