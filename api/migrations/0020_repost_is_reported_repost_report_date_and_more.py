# Generated by Django 5.1.6 on 2025-03-22 20:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_alter_repost_content_alter_repost_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='repost',
            name='is_reported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='repost',
            name='report_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='repost',
            name='report_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='repost',
            name='reported_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reported_reposts', to='api.userprofile'),
        ),
        migrations.AddField(
            model_name='repost',
            name='share_counter',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
