
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager

import my_settings
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