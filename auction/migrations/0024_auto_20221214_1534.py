# Generated by Django 2.2.16 on 2022-12-14 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0023_auto_20221212_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='placement',
            name='deposit',
            field=models.IntegerField(default=300000, help_text='예약금'),
        ),
        migrations.AlterField(
            model_name='placement',
            name='placement_type',
            field=models.CharField(choices=[('crowdfunding', '일반티켓'), ('secretfunding', '경쟁티켓'), ('openfunding', '경매')], default='crowdfunding', help_text='경매 종류', max_length=20),
        ),
        migrations.AlterField(
            model_name='placement',
            name='placement_win',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='placement_win', to='auction.PlacementBid'),
        ),
    ]
