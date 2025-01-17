# Generated by Django 2.2.16 on 2022-08-31 02:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('auction', '0002_auto_20220831_0231'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('artist', '0002_auto_20220831_0231'),
    ]

    operations = [
        migrations.AddField(
            model_name='placementbid',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='placement',
            name='placement_artist',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='auction.AuctionArtist'),
        ),
        migrations.AddField(
            model_name='placement',
            name='placement_win',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='placement_win', to='auction.PlacementBid'),
        ),
        migrations.AddField(
            model_name='placement',
            name='placement_win_crowdfunding',
            field=models.ManyToManyField(blank=True, related_name='placement_win_crowdfunding', to='auction.Donation'),
        ),
        migrations.AddField(
            model_name='donation',
            name='orderitem',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donation', to='core.OrderItems'),
        ),
        migrations.AddField(
            model_name='donation',
            name='placement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Placement'),
        ),
        migrations.AddField(
            model_name='donation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='autobid',
            name='placement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Placement'),
        ),
        migrations.AddField(
            model_name='autobid',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='auctionauthorization',
            name='placement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='auctionauthorization', to='auction.Placement'),
        ),
        migrations.AddField(
            model_name='auctionauthorization',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='auctionartist',
            name='artist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='artist.Artists'),
        ),
    ]
