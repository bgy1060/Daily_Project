from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager

import my_settings
from admin_page.models import AdminCategory
from notice_board.models import Point_List, NoticeBoard, Comment
from users.models import CustomUser, Register
from company.models import Company

import AES

User = get_user_model()


class EmptySerializer(serializers.Serializer):
    pass


class UserListSerializer(serializers.ModelSerializer):
    total_point = serializers.SerializerMethodField()
    num_post = serializers.SerializerMethodField()
    num_comment = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'total_point', 'num_post', 'num_comment')

    def get_total_point(self, obj):
        try:
            total_point = Point_List.objects.filter(uid=obj).order_by('-id')[0].total_point
            return total_point
        except:
            return 0

    def get_num_post(self, obj):
        try:
            return NoticeBoard.objects.filter(uid=obj).count()
        except:
            return 0

    def get_num_comment(self, obj):
        try:
            return Comment.objects.filter(uid=obj).count()
        except:
            return 0


class PointListSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Point_List
        fields = ('id', 'point', 'total_point', 'date', 'detail_action', 'action', 'email')

    def get_action(self, obj: Point_List):
        return obj.action_id.action

    def get_email(self, obj: Point_List):
        return obj.uid.email


class CategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdminCategory
        fields = ('category_id', 'category_name', 'parent_category_id')