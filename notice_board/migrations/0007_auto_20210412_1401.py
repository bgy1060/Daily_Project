# Generated by Django 3.1.7 on 2021-04-12 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notice_board', '0006_auto_20210412_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='order',
            field=models.IntegerField(unique=True),
        ),
    ]
