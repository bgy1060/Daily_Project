# Generated by Django 3.1.7 on 2021-04-29 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20210429_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='code',
            field=models.CharField(max_length=10),
        ),
    ]
