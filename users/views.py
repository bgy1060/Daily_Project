# Create your views here.
from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination

from datetime import datetime
from notice_board.models import *
from . import serializers
from .serializers import CompanyRegisterSerializer, CompanySerializer, UserInfoSerializer, PointSerializer, PointListSerializer
from .utils import get_and_authenticate_user, create_user_account
from django.utils import timezone

import base64
import my_settings
from drf_yasg import openapi

import uuid
import codecs
import AES

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
                    return Response(data={"Invitation Code is invalid!"}, status=status.HTTP_400_BAD_REQUEST)
            point_action = Point_action.objects.get(action='친구 가입')

            if Point_List.objects.filter(uid=uid, date__year=timezone.now().year,
                                         date__month=timezone.now().month,
                                         date__day=timezone.now().day,
                                         action_id=point_action.id).count() >= point_action.limit_number_of_day:
                pass
            else:
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
        print(query_set)
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
        """ USER 포인트 사용 내역 출력 [token required]"""
        start = datetime.strptime(request.data['start'], "%Y-%m-%d")
        end = datetime.strptime(request.data['end'], "%Y-%m-%d")

        paginator = PageNumberPagination()
        paginator.page_size = request.data['page_size']
        query_set = Point_List.objects.filter(uid=request.user.id,
                                              date__year__gte=start.year,
                                              date__month__gte=start.month,
                                              date__day__gte=start.day,
                                              date__year__lte=end.year,
                                              date__month__lte=end.month,
                                              date__day__lte=end.day).order_by("-id")
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
        serializer = CompanyRegisterSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)


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
