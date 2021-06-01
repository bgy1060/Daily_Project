
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


class EmptySerializer(serializers.Serializer):
    pass