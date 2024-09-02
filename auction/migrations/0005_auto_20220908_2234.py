# Generated by Django 2.2.16 on 2022-09-08 22:34

import auction.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20220908_2234'),
        ('auction', '0004_auto_20220908_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='placement',
            name='questionnaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Questionnaire'),
        ),
        migrations.AddField(
            model_name='placement',
            name='secret_video',
            field=models.FileField(blank=True, help_text='Unboxing list video', null=True, upload_to=auction.models.custom_video_path),
        ),
        migrations.AddField(
            model_name='placement',
            name='thumbnail',
            field=models.ImageField(blank=True, help_text='Thumbnail Image', null=True, upload_to=auction.models.custom_etc_path),
        ),
        migrations.AddField(
            model_name='placement',
            name='title',
            field=models.TextField(default='title', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='placement',
            name='unboxing_video_mp4',
            field=models.FileField(blank=True, help_text='Unboxing list video', null=True, upload_to=auction.models.custom_video_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4'])]),
        ),
        migrations.AddField(
            model_name='placement',
            name='youtube_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='auctionartist',
            name='E_name',
            field=models.TextField(default='AUCTION 아티스트 영어이름', max_length=255),
        ),
        migrations.AlterField(
            model_name='auctionartist',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Auction 아티스트 이미지', upload_to='Auction/avatar/'),
        ),
        migrations.AlterField(
            model_name='auctionartist',
            name='description',
            field=models.TextField(default='AUCTION 아티스트 소개'),
        ),
        migrations.AlterField(
            model_name='auctionartist',
            name='description_oneoff',
            field=models.TextField(default='AUCTION 아티스트 한줄'),
        ),
        migrations.AlterField(
            model_name='auctionartist',
            name='name',
            field=models.TextField(default='AUCTION 아티스트 한국이름', max_length=255),
        ),
        migrations.AlterField(
            model_name='placement',
            name='placement_win',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='placement_win', to='auction.PlacementBid'),
        ),
        migrations.AlterField(
            model_name='placement',
            name='unit_price',
            field=models.IntegerField(default=50000, help_text='크라우드 펀딩가 or 응찰단위'),
        ),
        migrations.AddField(
            model_name='oney',
            name='placementmemory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oneys', to='auction.PlacementMemory'),
        ),
    ]
