# Generated by Django 4.0.4 on 2022-06-25 04:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '0017_announcements_all_announcements_officials_only'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='announcements',
            name='all',
        ),
    ]
