# Generated by Django 2.2.16 on 2022-09-08 22:34

import auction.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0003_auto_20220831_0231'),
    ]

    operations = [
        migrations.CreateModel(
            name='Oney',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='워니의 성함을 입력해주세요', max_length=10)),
                ('comment', models.CharField(help_text='워니의 코멘트를 입력해주세요', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='donation',
            options={'ordering': ['placement', '-updated']},
        ),
        migrations.RenameField(
            model_name='autobid',
            old_name='modified',
            new_name='updated',
        ),
        migrations.RenameField(
            model_name='donation',
            old_name='donation_created',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='donation',
            old_name='donation_modified',
            new_name='updated',
        ),
        migrations.RenameField(
            model_name='placement',
            old_name='placement_category',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='placement',
            old_name='placement_created',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='placement',
            old_name='placement_modified',
            new_name='updated',
        ),
        migrations.RenameField(
            model_name='placementbid',
            old_name='placementbid_created',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='placementbid',
            old_name='placementbid_modified',
            new_name='updated',
        ),
        migrations.RenameField(
            model_name='placementmemory',
            old_name='celeb',
            new_name='celeb_name',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='orderitem',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='is_crowdfunding',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='is_crowdfunding_finish',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='mp4_video',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='placement_description',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='placement_title',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='placement_title_english',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='thumbnail_video',
        ),
        migrations.RemoveField(
            model_name='placement',
            name='webm_video',
        ),
        migrations.RemoveField(
            model_name='placementbid',
            name='orderitem',
        ),
        migrations.RemoveField(
            model_name='placementmemory',
            name='oney',
        ),
        migrations.RemoveField(
            model_name='placementmemory',
            name='oney_comment',
        ),
        migrations.AddField(
            model_name='auctionartist',
            name='description_info',
            field=models.TextField(default='AUCTION 아티스트 약력'),
        ),
        migrations.AddField(
            model_name='placement',
            name='d_day',
            field=models.DateTimeField(blank=True, help_text='만남 날짜', null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='d_place',
            field=models.CharField(blank=True, help_text='만남 장소', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='description',
            field=models.TextField(default='description', max_length=400),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='placement',
            name='detail_1',
            field=models.TextField(blank=True, help_text='펀딩상세 1', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='detail_1_title',
            field=models.TextField(blank=True, help_text='펀딩상세 1 타이틀', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='detail_2',
            field=models.TextField(blank=True, help_text='펀딩상세 2', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='detail_2_title',
            field=models.TextField(blank=True, help_text='펀딩상세 2 타이틀', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='detail_3',
            field=models.TextField(blank=True, help_text='펀딩상세 3', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='detail_3_title',
            field=models.TextField(blank=True, help_text='펀딩상세 3 타이틀', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='duration',
            field=models.CharField(blank=True, help_text='만남 시간', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='etc_1',
            field=models.TextField(blank=True, help_text='수익금 지원 공지', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='placement',
            name='image_1',
            field=models.ImageField(blank=True, help_text='상품 설명 이미지 1', null=True, upload_to=auction.models.custom_etc_path),
        ),
        migrations.AddField(
            model_name='placement',
            name='image_2',
            field=models.ImageField(blank=True, help_text='상품 설명 이미지 2', null=True, upload_to=auction.models.custom_etc_path),
        ),
        migrations.AddField(
            model_name='placement',
            name='image_3',
            field=models.ImageField(blank=True, help_text='상품 설명 이미지 3', null=True, upload_to=auction.models.custom_etc_path),
        ),
        migrations.AddField(
            model_name='placement',
            name='m_banner_video_mp4',
            field=models.FileField(blank=True, help_text='Mobile mp4 VIDEO', null=True, upload_to=auction.models.custom_video_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4'])]),
        ),
        migrations.AddField(
            model_name='placement',
            name='pc_banner_video_mp4',
            field=models.FileField(blank=True, help_text='PC mp4 VIDEO', null=True, upload_to=auction.models.custom_video_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4'])]),
        ),
    ]
