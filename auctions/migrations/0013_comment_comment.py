# Generated by Django 4.1.1 on 2023-01-10 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_listing_photo_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment',
            field=models.TextField(default='Poggers', max_length=500),
            preserve_default=False,
        ),
    ]
