# Create your views here.
from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from . import serializers
from .utils import get_and_authenticate_user, create_user_account
from django.utils import timezone

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {
        'login': serializers.UserLoginSerializer,
        'register': serializers.UserRegisterSerializer,
        'password_change': serializers.PasswordChangeSerializer,
        'withdrawal': serializers.WithdrawalSerializer,
    }

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)
        data = serializers.LoginSerializer(user).data
        if data['withdrawal_status'] == True:
            data = {"There is no member information."}
        else :
            data = serializers.LoginSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        data = {"Password change successful!"}
        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
    def withdrawal(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.withdrawal_status =1
        request.user.withdrawal_date = timezone.now()
        request.user.save()

        data = {"Membership withdrawal success"}
        return Response(data = data, status=status.HTTP_200_OK )

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


