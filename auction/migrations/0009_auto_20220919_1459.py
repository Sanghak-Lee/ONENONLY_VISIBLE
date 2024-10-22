# Generated by Django 2.2.4 on 2022-09-19 14:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auction', '0008_placementmemory_history_background'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auctionartist',
            name='artist',
        ),
        migrations.AddField(
            model_name='auctionartist',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='placement',
            name='placement_artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='auction.AuctionArtist'),
        ),
    ]
