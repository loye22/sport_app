# Generated by Django 5.1.6 on 2025-07-12 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_notification_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='repost',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
