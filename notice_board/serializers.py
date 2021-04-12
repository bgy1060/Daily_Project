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

    class Meta:
        model = NoticeBoard
        fields = ('post_id','user','title', 'date', 'views', 'like', 'dislike', 'category_id')

    def get_user(self,obj: User):
        return obj.uid.email


class DetailPostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = NoticeBoard
        fields = ('post_id', 'user', 'title', 'content', 'date', 'views', 'like', 'dislike', 'category_id')

    def get_user(self, obj: User):
        return obj.uid.email


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('comment_id', 'user', 'comment_content', 'date', 'like', 'dislike', 'post_id', 'parent_comment')

    def get_user(self, obj: User):
        return obj.uid.email


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_id', 'category_name')


class FAQListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ('id', 'question', 'answer', 'view', 'order')