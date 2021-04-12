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
from .serializers import CompanyRegisterSerializer,CompanySerializer,UserInfoSerializer
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
        """ USER 로그인 --- User 로그인 : email과 password를 전송하면 토큰 발행 """
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
        """ USER 등록 --- 새로운 User 회원가입 : 개인정보 입력 후 가입 가능"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        """ USER 로그아웃 """
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
    def password_change(self, request):
        """ USER 비민번호 변경 --- 기존 비밀번호와 변경할 비밀번호를 입력 후 비밀번호 변경 [token required]"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        data = {"Password change successful!"}
        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
    def withdrawal(self, request):
        """ 회원탈퇴 [token required]"""
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        request.user.withdrawal_status = 1
        request.user.withdrawal_date = timezone.now()
        request.user.save()

        data = {"Membership withdrawal success"}
        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def user_info(self, request):
        """ USER 정보 리스트 출력 --- uid 번호와 USER email 정보 전송"""
        query_set = User.objects.all()
        print(query_set)
        serializer = UserInfoSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

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
        """ 회사 목룍 가져오기"""
        query_set = Company.objects.all()
        serializer = CompanySerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)


    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def company_register(self, request):
        """ 회사 등록 : 사용자가 가입한 P2P 사이트의 id와 pw를 입력하여 가입 회사 등록 [token required]"""
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
        """ 사용자가 등록한 회사 목록 출력 [token required] """
        query_set = request.user.register_set.all()
        print(query_set)
        serializer = CompanyRegisterSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)
