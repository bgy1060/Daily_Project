# Generated by Django 3.1.7 on 2021-06-03 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_page', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admincategory',
            name='parent_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='admin_page.admincategory'),
        ),
    ]
