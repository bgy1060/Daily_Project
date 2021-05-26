from abc import ABC

from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager

import my_settings
from notice_board.models import Point_List
from users.models import CustomUser, Register
from company.models import Company

import AES


User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)


class LoginSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'withdrawal_status', 'auth_token')

    def get_auth_token(self, obj):
        token = Token.objects.get(user=obj)
        return token.key


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'auth_token')

    def get_auth_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key


class EmptySerializer(serializers.Serializer):
    pass


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if user:
            raise serializers.ValidationError("Email is already taken")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Current password does not match')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class WithdrawalSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=300, required=True)


class CompanyRegisterSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Register
        fields = (
            'uid',
            'email',
            'company_id',
            'company_name',
            'nickname'
        )

    def get_email(self, obj: Register):
        return AES.AESCipher(bytes(my_settings.key)).decrypt(obj.username.strip()).decode()

    def get_company_name(self, obj: Register):
        return obj.company_id.company_name

    def get_nickname(self, obj: Register):
        return obj.company_id.nickname


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'company_name', 'nickname')


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point_List
        fields = ['total_point']


class PointListSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()

    class Meta:
        model = Point_List
        fields = ('point', 'total_point', 'date', 'detail_action', 'action', 'uid')

    def get_action(self, obj: Point_List):
        return obj.action_id.action


