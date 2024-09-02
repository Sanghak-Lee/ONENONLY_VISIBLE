# Generated by Django 2.2.16 on 2022-08-31 02:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auction', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='placementbid',
            name='orderitem',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='placementbid', to='core.OrderItems'),
        ),
        migrations.AddField(
            model_name='placementbid',
            name='placement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Placement'),
        ),
    ]
