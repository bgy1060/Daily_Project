# Generated by Django 3.1.7 on 2021-04-02 02:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bank', models.CharField(max_length=30)),
                ('account_holder', models.CharField(max_length=50)),
                ('deposit', models.DecimalField(decimal_places=0, max_digits=13)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
