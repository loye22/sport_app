# Generated by Django 5.1.6 on 2025-06-22 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_alter_notification_followed_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='receiver',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='followed',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='follower',
        ),
    ]
