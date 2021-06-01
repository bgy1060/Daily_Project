from django.shortcuts import render

# Create your views here.

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from . import serializers

User = get_user_model()


class AdminViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def is_admin(self, request):
        """ 관리자가 맞는지 확인 [token required] : 입력받은 토큰으로 관리자가 맞는지 확인"""
        if request.user.username == 'Admin':
            return Response(data={'Admin 페이지 접속 가능!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)
