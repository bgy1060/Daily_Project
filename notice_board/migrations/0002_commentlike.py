# Generated by Django 3.1.7 on 2021-04-09 16:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notice_board', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('like_dislike', models.BooleanField()),
                ('comment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notice_board.comment')),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'comment_like',
                'unique_together': {('uid', 'comment_id')},
            },
        ),
    ]
