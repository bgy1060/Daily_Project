# Generated by Django 3.1.7 on 2021-04-02 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_customuser_is_superuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='P2P_Company',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=45)),
                ('hompage_url', models.CharField(max_length=70)),
            ],
        ),
    ]
