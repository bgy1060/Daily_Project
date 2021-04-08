# Create your views here.
from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from company.models import Company
from . import serializers
from .serializers import CompanyRegisterSerializer,CompanySerializer
from .utils import get_and_authenticate_user, create_user_account
from django.utils import timezone

import base64
from Crypto import Random
from Crypto.Cipher import AES
import my_settings

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
        else:
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
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        request.user.withdrawal_status = 1
        request.user.withdrawal_date = timezone.now()
        request.user.save()

        data = {"Membership withdrawal success"}
        return Response(data=data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        raw = pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8')))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))


class RegisterViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @csrf_exempt
    @action(methods=['GET', ], detail=False)
    def company(self,request):
        query_set = Company.objects.all()
        serializer = CompanySerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)


    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def company_register(self, request):
        data = request.data
        print(data)
        try:
            company_id = Company.objects.get(id=int(data['company_id']))

            username = data['username']
            user_password = data['user_password']

            encrypted_username = AESCipher(bytes(my_settings.key)).encrypt(username)
            encrypted_user_password = AESCipher(bytes(my_settings.key)).encrypt(user_password)

            print(len(encrypted_username))
            print(encrypted_username)

            '''
            #------  decryption test  -------

            decrypted_data = AESCipher(bytes(my_settings.key)).decrypt(encrypted_user_password)
            print(decrypted_data.decode('utf-8'))
            decrypted_username = AESCipher(bytes(my_settings.key)).decrypt(encrypted_username)
            print(decrypted_username.decode('utf-8'))
            '''

            try:
                request.user.register_set.create(username=encrypted_username.decode('utf-8'), user_password=encrypted_user_password.decode('utf-8'),
                                                 company_id=company_id, uid=request.user.id)
                message = {"Information registration completed!"}
            except:
                message = {"This site has already been registered!"}

        except:
            message = {"Please enter your company name correctly"}

        return Response(data=message, status=status.HTTP_201_CREATED)


    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def registered_company(self, request):
        query_set = request.user.register_set.all()
        print(query_set)
        serializer = CompanyRegisterSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)
