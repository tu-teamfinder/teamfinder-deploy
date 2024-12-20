# Generated by Django 5.1.3 on 2024-12-14 14:36

import cloudinary.models
import teamfinder_app.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teamfinder_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=cloudinary.models.CloudinaryField(blank=True, default='fallback.png', max_length=255, null=True, validators=[teamfinder_app.validators.validate_file_size], verbose_name='image'),
        ),
    ]
