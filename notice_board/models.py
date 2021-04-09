from django.db import models
from users.models import *
from company.models import *


# Create your models here.

class NoticeBoard(models.Model):
    post_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=70, default="")
    content = models.TextField()
    date = models.DateTimeField()
    views = models.IntegerField(default=0)
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)

    class Meta:
        db_table = 'notice_board'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(NoticeBoard, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment_content = models.TextField()
    date = models.DateTimeField()
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)

    class Meta:
        db_table = 'comment'


class NoticeBoardLike(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(NoticeBoard, on_delete=models.CASCADE)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    like_dislike = models.BooleanField(null=False)

    class Meta:
        db_table = 'notice_board_like'
        unique_together = ['uid', 'post_id']


class CommentLike(models.Model):
    id = models.AutoField(primary_key=True)
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    like_dislike = models.BooleanField(null=False)

    class Meta:
        db_table = 'comment_like'
        unique_together = ['uid', 'comment_id']

