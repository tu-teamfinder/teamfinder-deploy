# Generated by Django 5.1.3 on 2024-11-14 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamfinder_app', '0002_alter_group_group_id_alter_message_message_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
