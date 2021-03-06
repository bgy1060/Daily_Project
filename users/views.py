# Create your views here.

import string
import random
import re

from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination

from notice_board.models import *
from . import serializers
from .serializers import CompanyRegisterSerializer, CompanySerializer, UserInfoSerializer, PointSerializer, \
    PointListSerializer
from .utils import get_and_authenticate_user, create_user_account
from django.utils import timezone

import base64
import my_settings
from drf_yasg import openapi

import uuid
import codecs
import AES
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from rest_framework.authtoken.models import Token
from django.db.models import Q

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
        if data['withdrawal_status']:
            data = {"There is no member information."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = serializers.LoginSerializer(user).data
            point_action = Point_action.objects.get(action='로그인')

            if Point_List.objects.filter(uid=data['id'], date__year=timezone.now().year,
                                         date__month=timezone.now().month,
                                         date__day=timezone.now().day,
                                         action_id=point_action.id).count() >= point_action.limit_number_of_day:
                pass
            else:
                uid = CustomUser.objects.get(id=data['id'])
                try:
                    total_point = Point_List.objects.filter(uid=data['id']).order_by('-id')[0].total_point
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=total_point + point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='로그인',
                                              uid=uid)
                except:
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='로그인',
                                              uid=uid)

        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def register(self, request):
        """ USER 등록 --- 새로운 User 회원가입 : 개인정보 입력 후 가입 가능"""
        regex1 = re.compile(r'(?=.*[0-9])(?=.*[^\w\s]).*')
        regex2 = re.compile(r'(?=.*[0-9]).*')
        regex3 = re.compile(r'(?=.*[^\w\s]).*')

        if regex1.match(request.data['username']) is not None or regex2.match(request.data['username']) is not None or \
                regex3.match(request.data['username']) is not None:
            return Response(data={'username': ["이름에는 숫자나 특수문자를 포함할 수 없습니다."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        point_action = Point_action.objects.get(action='회원가입')
        uid = CustomUser.objects.get(id=data['id'])
        try:
            total_point = Point_List.objects.filter(uid=data['id']).order_by('-id')[0].total_point
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=total_point + point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='회원가입 축하 포인트',
                                      uid=uid)
        except:
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='회원가입 축하 포인트',
                                      uid=uid)

        try:
            if request.data['code']:
                try:
                    uid = CustomUser.objects.get(code=request.data['code'])
                except:
                    return Response(data={"ucode": ["Invitation Code is invalid!"]}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"회원가입 완료!"}, status=status.HTTP_201_CREATED)
            point_action = Point_action.objects.get(action='친구 가입')

            if Point_List.objects.filter(uid=uid, date__year=timezone.now().year,
                                         date__month=timezone.now().month,
                                         date__day=timezone.now().day,
                                         action_id=point_action.id).count() >= point_action.limit_number_of_day:
                pass
            else:
                try:
                    total_point = Point_List.objects.filter(uid=uid).order_by('-id')[0].total_point
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=total_point + point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='초대 친구 가입 축하 포인트',
                                              uid=uid)

                except:
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='초대 친구 가입 축하 포인트',
                                              uid=uid)

            point_action = Point_action.objects.get(action='친구 가입')
            uid = CustomUser.objects.get(id=data['id'])

            try:
                total_point = Point_List.objects.filter(uid=data['id']).order_by('-id')[0].total_point
                Point_List.objects.create(point=point_action.point_value,
                                          total_point=total_point + point_action.point_value,
                                          date=timezone.now(),
                                          action_id=point_action,
                                          detail_action='초대 친구 가입 축하 포인트',
                                          uid=uid)
            except:
                Point_List.objects.create(point=point_action.point_value,
                                          total_point=point_action.point_value,
                                          date=timezone.now(),
                                          action_id=point_action,
                                          detail_action='초대 친구 가입 축하 포인트',
                                          uid=uid)
        except:
            pass

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
        serializer = UserInfoSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'page_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='한 페이지에 표시할 내역 수'),
            'start': openapi.Schema(type=openapi.TYPE_INTEGER, description='내역 시작 날짜'),
            'end': openapi.Schema(type=openapi.TYPE_INTEGER, description='내역 끝 날짜'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def my_point_list(self, request):
        """ USER 포인트 내역 출력 [token required]"""
        start = datetime.strptime(request.data['start'], "%Y-%m-%d")
        end = datetime.strptime(request.data['end'], "%Y-%m-%d")

        paginator = PageNumberPagination()
        paginator.page_size = request.data['page_size']
        query_set = Point_List.objects.filter(uid=request.user.id,
                                              date__range=[start, end + timedelta(days=1)]).order_by("-id")

        result_page = paginator.paginate_queryset(query_set, request)
        serializer = PointListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def my_point(self, request):
        """ USER 현재 포인트 [token required]"""
        query_set = Point_List.objects.filter(uid=request.user.id).order_by("-id").first()
        serializer = PointSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def get_image(self, request):
        """ 사용자 프로필 사진 가져오기 - 프로필이 없을 경우 기본 이미지로 [token required]"""
        uid = request.user.id
        try:
            with open('./user_profile/' + str(uid) + '_profile.png', 'rb') as f:
                file_data = f.read()

        except IOError:
            with open('./user_profile/main_profile.png', 'rb') as f:
                file_data = f.read()

        response = HttpResponse(file_data, content_type="image/png")
        return response

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def image_upload(self, request):
        """ 사용자 프로필 사진 가져오기 - 프로필이 없을 경우 기본 이미지로 [token required]"""
        uid = request.user.id
        img = request.FILES['filename']

        import os
        with open(os.path.join('./user_profile/', str(uid) + '_profile.png'), mode='wb') as file:
            for chunk in img.chunks():
                file.write(chunk)

        return Response(status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class RegisterViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @csrf_exempt
    @action(methods=['GET', ], detail=False)
    def company(self, request):
        """ 회사 목룍 가져오기"""
        query_set = Company.objects.all()
        serializer = CompanySerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='등록하고 싶은 회사 ID'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='P2P 회사(company_id를 가진 회사) 아이디'),
            'user_password': openapi.Schema(type=openapi.TYPE_STRING, description='P2P 회사(company_id를 가진 회사) 비밀번호'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def company_register(self, request):
        """ 회사 등록 : 사용자가 가입한 P2P 사이트의 id와 pw를 입력하여 가입 회사 등록 [token required]"""
        data = request.data
        try:
            company_id = Company.objects.get(id=int(data['company_id']))

            username = data['username']
            user_password = data['user_password']

            encrypted_username = AES.AESCipher(bytes(my_settings.key)).encrypt(username)
            encrypted_user_password = AES.AESCipher(bytes(my_settings.key)).encrypt(user_password)

            '''
            #------  decryption test  -------

            decrypted_data = AESCipher(bytes(my_settings.key)).decrypt(encrypted_user_password)
            print(decrypted_data.decode('utf-8'))
            decrypted_username = AESCipher(bytes(my_settings.key)).decrypt(encrypted_username)
            print(decrypted_username.decode('utf-8'))
            '''

            try:
                request.user.register_set.create(username=encrypted_username.decode('utf-8'),
                                                 user_password=encrypted_user_password.decode('utf-8'),
                                                 company_id=company_id, uid=request.user.id)

                point_action = Point_action.objects.get(action='업체 연동')

                if Point_List.objects.filter(uid=request.user.id, date__year=timezone.now().year,
                                             date__month=timezone.now().month,
                                             date__day=timezone.now().day,
                                             action_id=point_action.id).count() >= point_action.limit_number_of_day:
                    pass
                else:
                    uid = CustomUser.objects.get(id=request.user.id)
                    try:
                        total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
                        Point_List.objects.create(point=point_action.point_value,
                                                  total_point=total_point + point_action.point_value,
                                                  date=timezone.now(),
                                                  action_id=point_action,
                                                  detail_action='새로운 P2P 업체 연동 감사 포인트',
                                                  uid=uid)
                    except:
                        Point_List.objects.create(point=point_action.point_value,
                                                  total_point=point_action.point_value,
                                                  date=timezone.now(),
                                                  action_id=point_action,
                                                  detail_action='새로운 P2P 업체 연동 감사 포인트',
                                                  uid=uid)
                message = {0: "Information registration completed!"}
            except:
                message = {1: "This site has already been registered!"}

        except:
            message = {2: "Please enter your company id correctly"}

        return Response(data=message, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'search_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='검색 키워드'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def registered_company(self, request):
        """ 사용자가 등록한 회사 목록 출력 [token required]
            사용자가 검색한 회사 목록을 보고싶다면 search_keyword에 검색 키워드 작성.
        """

        search_keyword = request.data['search_keyword']

        query_set = request.user.register_set.all().order_by('company_id__company_name')
        if search_keyword:
            query_set = query_set.filter(Q(company_id__company_name__icontains=search_keyword))

        serializer = CompanyRegisterSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='등록 해지를 원하는 회사 ID'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def company_delete(self, request):
        """ 등록 회사 삭제 : 사용자가 등록한 P2P 사이트 로그인 정보 삭제 [token required]"""
        data = request.data

        company_id = Company.objects.get(id=int(data['company_id']))

        try:
            Register.objects.get(company_id=company_id, uid=request.user.id).delete()
        except:
            message = {"This site has already been deleted!"}
            return Response(data=message, status=status.HTTP_404_NOT_FOUND)

        point_action = Point_action.objects.get(action='업체 연동 해지')
        uid = CustomUser.objects.get(id=request.user.id)
        try:
            total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=total_point + point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='P2P 업체 연동 해지 차감 포인트',
                                      uid=uid)
        except:
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='P2P 업체 연동 해지 차감 포인트',
                                      uid=uid)
        message = {"Delete_Ok"}

        return Response(data=message, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='로그인 정보 업데이트를 원하는 회사 ID'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='P2P 회사(company_id를 가진 회사) 아이디'),
            'user_password': openapi.Schema(type=openapi.TYPE_STRING, description='P2P 회사(company_id를 가진 회사) 비밀번호'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def company_update(self, request):
        """ 등록 회사 로그인 정보 업데이트 : 사용자가 등록한 P2P 사이트 로그인 정보 업데이트 [token required]"""
        data = request.data

        company_id = Company.objects.get(id=int(data['company_id']))

        try:
            username = data['username']
            encrypted_username = AES.AESCipher(bytes(my_settings.key)).encrypt(username).decode('utf-8')

            try:  # id, pwd 모두 업데이트
                user_password = data['user_password']
                encrypted_user_password = AES.AESCipher(bytes(my_settings.key)).encrypt(user_password).decode('utf-8')

                register = Register.objects.get(company_id=company_id, uid=request.user.id)
                register.username = encrypted_username
                register.user_password = encrypted_user_password
                register.save()

                message = {"ID & PWD Udate_Ok"}

            except:  # id만 업데이트
                register = Register.objects.get(company_id=company_id, uid=request.user.id)
                register.username = encrypted_username
                register.save()

                message = {"ID Udate_Ok"}

        except:  # 비밀번호만 업데이트
            try:
                user_password = data['user_password']
                encrypted_user_password = AES.AESCipher(bytes(my_settings.key)).encrypt(user_password)

                register = Register.objects.get(company_id=company_id, uid=request.user.id)
                register.user_password = encrypted_user_password
                register.save()

                message = {"PWD Udate_Ok"}
            except:  # 아이디 비밀번호 둘 다 없는 경우
                message = {"Please enter id & pwd"}

        return Response(data=message, status=status.HTTP_200_OK)


class CodeViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def create_code(self, request):
        """친구 초대 코드 생성 [token required]"""
        if request.user.code is None:
            while True:
                try:
                    request.user.code = base64.urlsafe_b64encode(
                        codecs.encode(uuid.uuid4().bytes, "base64").rstrip()
                    ).decode()[:8]
                    request.user.save()
                    break
                except:
                    pass
        else:
            pass

        data = request.user.code
        return Response(data=data, status=status.HTTP_201_CREATED)

    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def get_point(self, request):
        """친구 초대 메시지 전송 완료 후 포인트 지급 [token required]"""

        point_action = Point_action.objects.get(action='친구 초대')
        if Point_List.objects.filter(uid=request.user.id, date__year=timezone.now().year,
                                     date__month=timezone.now().month,
                                     date__day=timezone.now().day,
                                     action_id=point_action.id).count() >= point_action.limit_number_of_day:
            data = "You have exceeded the number of times you can receive points."
            pass
        else:
            uid = CustomUser.objects.get(id=request.user.id)
            try:
                total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
                Point_List.objects.create(point=point_action.point_value,
                                          total_point=total_point + point_action.point_value,
                                          date=timezone.now(),
                                          action_id=point_action,
                                          detail_action='친구 초대',
                                          uid=uid)
            except:
                Point_List.objects.create(point=point_action.point_value,
                                          total_point=point_action.point_value,
                                          date=timezone.now(),
                                          action_id=point_action,
                                          detail_action='친구 초대',
                                          uid=uid)
            data = "Point payment completed!"

        return Response(data=data, status=status.HTTP_201_CREATED)


class ForgetPWDViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호 찾기를 원하는 사용자의 이메일'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, )
    def email_auth_num(self, request):
        """ 비밀번호 변경 토큰 생성 -> 토큰 생성 후 User 테이블 forget_pwd_token에 저장 -> 이메일로 토큰 전송"""
        email = request.data['email']
        user = User.objects.get(email=email)

        if user.withdrawal_status:
            return Response(data={"탈퇴 회원"}, status=status.HTTP_400_BAD_REQUEST)

        LENGTH = 8
        string_pool = string.ascii_letters + string.digits
        auth_num = ""
        for i in range(LENGTH):
            auth_num += random.choice(string_pool)

        user.forget_pwd_token = auth_num
        user.save()

        email_content = render_to_string('verify_email.html', {"password_token": auth_num})
        email = EmailMessage(
            'Daily Now 비밀번호 찾기 인증 메일.',
            email_content,
            my_settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        email.content_subtype = "html"
        email.send()

        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='사용자가 메일로 받은 임의의 토큰 값'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, )
    def is_pwd_token(self, request):
        """ 토큰값이 유효한 값인지 확인"""
        token = request.data['token']
        try:
            user = User.objects.get(forget_pwd_token=token)
            user_token = Token.objects.get(user_id=user.id)
            return Response(data=str(user_token), status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='변경할 비밀번호 입력'),

        }))
    @csrf_exempt
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
    def password_reset(self, request):
        """ USER 비민번호 변경 --- 변경할 비밀번호를 입력 후 비밀번호 변경 [token required]"""
        pwd = request.data['new_password']
        if len(pwd) < 8:
            data = {"비밀번호는 8자리 이상!"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(pwd)
        request.user.save()
        data = {"Password change successful!"}
        return Response(data=data, status=status.HTTP_200_OK)
