# Generated by Django 4.0.4 on 2022-06-17 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '0011_alter_student_regd_no_alter_student_roll_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=5.0, max_digits=3),
        ),
    ]
