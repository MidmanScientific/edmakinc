# Generated by Django 5.0.1 on 2024-11-09 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edmakFeatures', '0002_alter_courserequest_course'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='name',
            new_name='course',
        ),
    ]
