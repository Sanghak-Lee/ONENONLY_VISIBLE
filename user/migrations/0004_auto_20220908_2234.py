# Generated by Django 2.2.16 on 2022-09-08 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0004_auto_20220908_2234'),
        ('user', '0003_verification_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='artist_like',
        ),
        migrations.RemoveField(
            model_name='users',
            name='review_like',
        ),
        migrations.AddField(
            model_name='users',
            name='plike',
            field=models.ManyToManyField(blank=True, related_name='plikes', to='auction.Placement'),
        ),
        migrations.AlterField(
            model_name='users',
            name='alarm',
            field=models.ManyToManyField(blank=True, related_name='alarms', to='auction.Placement'),
        ),
        migrations.AlterField(
            model_name='users',
            name='encore',
            field=models.ManyToManyField(blank=True, related_name='encores', to='auction.Placement'),
        ),
    ]