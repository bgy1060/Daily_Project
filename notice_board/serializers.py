from django.db.models import Count
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager

from users.models import CustomUser, Register
from company.models import Company
from .models import *

User = get_user_model()


class PostListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = NoticeBoard
        fields = ('post_id','user','title', 'date', 'views','comment_count', 'like', 'dislike', 'category_id', 'uid')

    def get_user(self, obj: User):
        return obj.uid.email

    def get_comment_count(self, obj: NoticeBoard):
        return Comment.objects.filter(post_id=obj.post_id).count()


class DetailPostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    is_like_dislike = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()
    like_dislike = serializers.SerializerMethodField()

    class Meta:
        model = NoticeBoard
        fields = ('post_id', 'user', 'title', 'content', 'date', 'views', 'like', 'dislike', 'category_id', 'is_like_dislike','like_dislike','editable')

    def get_user(self, obj: User):
        return obj.uid.email

    def get_is_like_dislike(self, obj: User):
        return self.context[0]

    def get_editable(self, obj: User):
        if self.context[1] == obj.uid.id:
            return True
        else:
            return False

    def get_like_dislike(self, obj: User):
        return self.context[2]


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    is_like_dislike = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()
    like_dislike = serializers.SerializerMethodField()
    num_child = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('comment_id', 'user', 'comment_content', 'date', 'like', 'dislike', 'post_id', 'parent_comment','is_like_dislike','like_dislike', 'editable', 'num_child')

    def get_user(self, obj: User):
        return obj.uid.email

    def get_is_like_dislike(self, obj: Comment):
        try:
            obj.commentlike_set.get(uid=self.context)
            return True
        except:
            return False

    def get_editable(self, obj: User):
        if self.context == obj.uid.id:
            return True
        else:
            return False

    def get_like_dislike(self, obj: CommentLike):
        try:
            return int(obj.commentlike_set.get(uid=self.context).like_dislike)
        except:
            return-1

    def get_num_child(self, obj: Comment):
        return Comment.objects.filter(parent_comment_id=obj.comment_id).count()


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_id', 'category_name')


class FAQListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ('id', 'question', 'answer', 'view', 'order')