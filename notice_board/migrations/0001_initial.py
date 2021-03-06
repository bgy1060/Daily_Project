# Generated by Django 3.1.7 on 2021-04-09 15:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeBoard',
            fields=[
                ('post_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(default='', max_length=70)),
                ('content', models.TextField()),
                ('date', models.DateTimeField()),
                ('views', models.IntegerField(default=0)),
                ('like', models.IntegerField(default=0)),
                ('dislike', models.IntegerField(default=0)),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notice_board',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.AutoField(primary_key=True, serialize=False)),
                ('comment_content', models.TextField()),
                ('date', models.DateTimeField()),
                ('like', models.IntegerField(default=0)),
                ('dislike', models.IntegerField(default=0)),
                ('parent_comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='notice_board.comment')),
                ('post_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notice_board.noticeboard')),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'comment',
            },
        ),
        migrations.CreateModel(
            name='NoticeBoardLike',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('like_dislike', models.BooleanField()),
                ('post_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notice_board.noticeboard')),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notice_board_like',
                'unique_together': {('uid', 'post_id')},
            },
        ),
    ]
