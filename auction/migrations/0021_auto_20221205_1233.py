# Generated by Django 2.2.16 on 2022-12-05 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0020_auto_20221129_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oney',
            name='comment',
            field=models.CharField(help_text='워니의 코멘트를 입력해주세요', max_length=200),
        ),
        migrations.AlterField(
            model_name='oney',
            name='name',
            field=models.CharField(help_text='워니의 성함을 입력해주세요', max_length=20),
        ),
        migrations.AlterField(
            model_name='placementmemory',
            name='celeb_comment',
            field=models.CharField(help_text='셀럽의 코멘트를 입력해주세요', max_length=200),
        ),
        migrations.AlterField(
            model_name='placementmemory',
            name='celeb_name',
            field=models.CharField(help_text='셀럽의 성함을 입력해주세요', max_length=20),
        ),
    ]