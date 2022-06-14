# Generated by Django 4.0.4 on 2022-06-11 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_alter_outing_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='outing',
            name='status',
            field=models.CharField(choices=[('In Outing', 'In Outing'), ('Closed', 'Closed')], default='NA', max_length=9),
        ),
        migrations.AlterField(
            model_name='outing',
            name='permission',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Granted', 'Granted'), ('Rejected', 'Rejected'), ('Revoked', 'Revoked'), ('Pending Extension', 'Pending Extension'), ('Processing Extension', 'Processing Extension')], default='Pending', max_length=20),
        ),
    ]