# Generated by Django 3.1.7 on 2021-05-26 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='username',
            new_name='name',
        ),
    ]
