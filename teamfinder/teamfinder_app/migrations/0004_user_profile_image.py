# Generated by Django 5.1.3 on 2024-11-16 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamfinder_app', '0003_faculty_major_remove_requirement_req_faculty_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, default='fallback.png', null=True, upload_to='images/'),
        ),
    ]
