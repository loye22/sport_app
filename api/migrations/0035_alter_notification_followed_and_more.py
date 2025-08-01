# Generated by Django 5.1.6 on 2025-06-22 14:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_rename_user_notification_receiver_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='followed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications_as_followed', to='api.userprofile'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='follower',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications_as_follower', to='api.userprofile'),
        ),
    ]
