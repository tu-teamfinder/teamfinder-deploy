# Generated by Django 5.1.3 on 2024-12-14 19:29

import cloudinary.models
import teamfinder_app.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teamfinder_app', '0002_alter_userprofile_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=cloudinary.models.CloudinaryField(blank=True, default='v1734185337/images/fallback.jpg', max_length=255, null=True, validators=[teamfinder_app.validators.validate_file_size], verbose_name='image'),
        ),
    ]
