# Generated by Django 4.1.1 on 2023-01-10 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_listing_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='photo_url',
            field=models.URLField(blank=True, max_length=150),
        ),
    ]
