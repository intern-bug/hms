# Generated by Django 4.0.4 on 2022-06-17 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0011_alter_outing_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='outing',
            name='mess_rebate',
            field=models.CharField(choices=[('Enabled', 'Enabled'), ('Disabled', 'Disabled')], default='Disabled', max_length=9),
        ),
    ]
