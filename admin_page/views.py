from django.core.mail import EmailMessage

# Create your views here.

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import my_settings
from notice_board.models import Category, FAQ, Point_List, Point_action, Company
from . import serializers
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

from .models import AdminCategory
from .serializers import UserListSerializer, PointListSerializer, CategoryListSerializer
from django.utils import timezone
from django.db.models import Q

User = get_user_model()


class AdminViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def is_admin(self, request):
        """ 관리자가 맞는지 확인 [admin token required] : 입력받은 토큰으로 관리자가 맞는지 확인"""
        if request.user.username == 'Admin':
            return Response(data={'Admin 페이지 접속 가능!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def admin_category(self, request):
        """ 관리자 페이지 카테고리 전송 [admin token required] """
        if request.user.username == 'Admin':
            query_set = AdminCategory.objects.all()
            serializer = CategoryListSerializer(query_set, many=True)
            return JsonResponse(serializer.data, safe=False)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)


class UserManagementViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'page_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='한 페이지에 표시할 글 수'),
            'search_type': openapi.Schema(type=openapi.TYPE_STRING, description='이름/이메일/가입일 검색 가능'),
            'search_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='검색 키워드 or 날짜'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def user_list(self, request):
        """ 전체 회원 리스트 검색 및 보기 [admin token required] : 입력받은 토큰으로 관리자가 맞는지 확인 -> 관리자가 아니면 400에러
            serch_type에는 검색하고 싶은 종류를 입력 : username, email, date_joined를 선택할 수 있음
            search_keyword에는 검색하고 싶은 이름, 이메일, 가입 날짜 등의 정보를 입력
            검색 기능을 사용하지 않은 경우 search_type 과 search_keyword는 null로 세팅
        """

        if request.user.username == 'Admin':

            paginator = PageNumberPagination()
            paginator.page_size = request.data['page_size']
            search_type = request.data['search_type']
            search_keyword = request.data['search_keyword']

            if search_keyword and search_type:
                if search_type == 'username':
                    query_set = User.objects.filter(username=search_keyword)
                elif search_type == 'email':
                    query_set = User.objects.filter(email=search_keyword)
                elif search_type == 'date_joined':
                    date = datetime.strptime(search_keyword, "%Y-%m-%d")
                    query_set = User.objects.filter(date_joined__year=date.year,
                                                    date_joined__month=date.month,
                                                    date_joined__day=date.day)
            else:
                query_set = User.objects.all()

            result_page = paginator.paginate_queryset(query_set, request)
            serializer = UserListSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @action(methods=['GET', ], detail=False, permission_classes=[IsAuthenticated, ])
    def user_statics(self, request):
        """ 전체 회원 통계 정보 [admin token required] : 전체 회원 수, 신규 가입 수, 탈퇴 회원 수
        """

        if request.user.username == 'Admin':
            total_user = User.objects.filter(withdrawal_status=0).count()
            new_user = User.objects.filter(date_joined__year=timezone.now().year,
                                           date_joined__month=timezone.now().month,
                                           date_joined__day=timezone.now().day).count()
            withdrawal_user = User.objects.filter(withdrawal_status=1).count()

            return Response(
                data={'total_user': [total_user], 'new_user': [new_user], 'withdrawal_user': [withdrawal_user]},
                status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='삭제를 원하는 유저 이메일'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def user_delete(self, request):
        """ 회원 삭제 [admin token required] : 특정 회원정보 삭제
        """
        email = request.data['email']
        if request.user.username == 'Admin':
            user = User.objects.get(email=email)
            user.delete()
            return Response(data={'삭제 완료'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='업데이트를 원하는 유저 이메일'),
            'new_email': openapi.Schema(type=openapi.TYPE_STRING, description='업데이트 이메일'),
            'new_username': openapi.Schema(type=openapi.TYPE_STRING, description='업데이트 사용자 이름'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def user_info_update(self, request):
        """ 회원 정보 업데이트 [admin token required] : 특정 회원의 회원정보 업데이트 (회원의 이름과 이메일 정보 수정 가능)
        """
        if request.user.username == 'Admin':
            email = request.data['email']
            new_email = request.data['new_email']
            new_username = request.data['new_username']

            user = User.objects.get(email=email)

            if new_email and new_username:
                user.email = new_email
                user.username = new_username
                try:
                    user.save()
                except:
                    return Response(data={'중복된 이메일'}, status=status.HTTP_400_BAD_REQUEST)

            elif new_email:
                user.email = new_email
                try:
                    user.save()
                except:
                    return Response(data={'중복된 이메일'}, status=status.HTTP_400_BAD_REQUEST)

            elif new_username:
                user.username = new_username
                user.save()
            return Response(data={'업데이트 완료'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'send_mail': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.TYPE_STRING,
                                        description='이메일을 전송하고 싶은 사용자의 이메일 주소 배열'),
            'email_title': openapi.Schema(type=openapi.TYPE_STRING, description='이메일 제목'),
            'email_content': openapi.Schema(type=openapi.TYPE_STRING, description='이메일 내용'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def send_mail(self, request):
        """ 특정 회원에게 이메일 전송 [admin token required]
        """
        send_mail = request.data['send_mail']
        email_title = request.data['email_title']
        email_content = request.data['email_content']

        if request.user.username == 'Admin':
            email = EmailMessage(
                email_title,
                email_content,
                my_settings.EMAIL_HOST_USER,
                to=send_mail
            )
            email.send()
            return Response(data={'메일 전송 완료'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)


class CategoryManagementViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'category_name': openapi.Schema(type=openapi.TYPE_STRING, description='추가할 카테고리 이름'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_category(self, request):
        """ 게시판 카테고리 추가 [admin token required]"""
        if request.user.username == 'Admin':
            category_name = request.data['category_name']
            category_id = Category.objects.all().last().category_id
            Category.objects.create(category_id=category_id + 1, category_name=category_name)
            return Response(data={'카테고리 추가 완료!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='변경할 카테고리 id'),
            'new_category_name': openapi.Schema(type=openapi.TYPE_STRING, description='변경할 카테고리 이름'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def update_category(self, request):
        """ 게시판 카테고리 이름 업데이트 [admin token required]"""
        if request.user.username == 'Admin':
            category_id = request.data['category_id']
            category_name = request.data['new_category_name']

            if Category.objects.filter(category_name=category_name).count() is not 0:
                return Response(data={'카테고리 이름 중복!'}, status=status.HTTP_400_BAD_REQUEST)

            category = Category.objects.get(category_id=category_id)
            category.category_name = category_name
            category.save()
            return Response(data={'카테고리 업데이트 완료!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)


class FAQManagementViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'question': openapi.Schema(type=openapi.TYPE_STRING, description='질문'),
            'answer': openapi.Schema(type=openapi.TYPE_STRING, description='답변'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_faq(self, request):
        """ FAQ 추가 [admin token required]"""
        if request.user.username == 'Admin':
            question = request.data['question']
            answer = request.data['answer']
            order = FAQ.objects.all().order_by('-order').first().order

            FAQ.objects.create(question=question, answer=answer, view=0, order=order + 1)

            return Response(data={'FAQ 추가 완료!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'faq_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='FAQ 아이디'),
            'new_question': openapi.Schema(type=openapi.TYPE_STRING, description='질문'),
            'new_answer': openapi.Schema(type=openapi.TYPE_STRING, description='답변'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def update_faq(self, request):
        """ FAQ 질문 or 답변 업데이트 [admin token required]"""
        if request.user.username == 'Admin':
            faq_id = request.data['faq_id']
            question = request.data['new_question']
            answer = request.data['new_answer']

            faq = FAQ.objects.get(id=faq_id)
            if question and answer:
                faq.question = question
                faq.answer = answer
                faq.save()

            elif question:
                faq.question = question
                faq.save()

            elif answer:
                faq.answer = answer
                faq.save()
            return Response(data={'FAQ 업데이트 완료!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'faq_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='FAQ 아이디'),
            'new_order': openapi.Schema(type=openapi.TYPE_INTEGER, description='질문 노출 순서'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def update_faq_order(self, request):
        """ FAQ 질문 노출 순서 변경 [admin token required]"""
        if request.user.username == 'Admin':
            faq_id = request.data['faq_id']
            order = request.data['new_order']

            faq = FAQ.objects.get(id=faq_id)

            faq.order = order
            try:
                faq.save()
            except:
                return Response(data={'중복된 순서!'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'FAQ 업데이트 완료!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)


class PointManagementViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'page_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='한 페이지에 표시할 글 수'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='포인트 내역을 보고싶은 사용자의 이메일 주소'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def point_list(self, request):
        """ 전체 회원 포인트 리스트 검색 및 보기 [admin token required] :
            email을 입력하여 특정 회원의 포인트 내역 조회 가능
            검색 기능을 사용하지 않은 경우 email 필드를 null로 세팅
        """

        if request.user.username == 'Admin':

            paginator = PageNumberPagination()
            paginator.page_size = request.data['page_size']
            email = request.data['email']

            if email:
                uid = User.objects.get(email=email).id
                query_set = Point_List.objects.filter(uid=uid).order_by('-id')
            else:
                query_set = Point_List.objects.all().order_by('-id')

            result_page = paginator.paginate_queryset(query_set, request)
            serializer = PointListSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'all': openapi.Schema(type=openapi.TYPE_INTEGER, description='전체 회원에에 포인트를 지급할지 여부'),
            'email': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.TYPE_STRING,
                                    description='포인트를 추가하고 싶은 사용자 이메일 주소'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_point(self, request):
        """ 회원 포인트 추가 [admin token required] :
            전체 회원에게 포인트를 추가할 경우 all 필드는 1로 email 필드는 null로 세팅
            특정 회원에게 포인트를 추가할 경우 all 필드는 0으로 email 필드는 포인트를 추가하고 싶은 사용자 이메일 배열로 세팅
        """

        if request.user.username == 'Admin':

            paginator = PageNumberPagination()
            paginator.page_size = request.data['page_size']
            email = request.data['email']

            if email:
                user = User.objects.filter(Q(email__in=email))
                for i in range(len(user)):
                    uid = User.objects.get(email=user[i].email)
                    point = Point_action.objects.get(action='관리자 수동 지급').point_value
                    action_id = Point_action.objects.get(action='관리자 수동 지급')
                    try:
                        total_point = Point_List.objects.filter(uid=uid).order_by('-id').first().total_point
                    except:
                        total_point = 0

                    Point_List.objects.create(point=point,
                                              total_point=total_point + point,
                                              date=timezone.now(),
                                              detail_action='관리자 수동 지급 포인트',
                                              action_id=action_id,
                                              uid=uid)
            else:
                for i in range(len(User.objects.filter(withdrawal_status=0))):
                    uid = User.objects.filter(withdrawal_status=0)[i]
                    point = Point_action.objects.get(action='관리자 수동 지급').point_value
                    action_id = Point_action.objects.get(action='관리자 수동 지급')
                    try:
                        total_point = Point_List.objects.filter(uid=uid).order_by('-id').first().total_point
                    except:
                        total_point = 0

                    Point_List.objects.create(point=point,
                                              total_point=total_point + point,
                                              date=timezone.now(),
                                              detail_action='관리자 수동 지급 포인트',
                                              action_id=action_id,
                                              uid=uid)

            return Response(data={'포인트 지급 완료!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)


class CompanyManagementViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='추가할 회사 이름'),
            'homepage_url': openapi.Schema(type=openapi.TYPE_STRING, description='추가할 회사 홈페이지 주소'),
            'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='추가할 회사 닉네임'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_company(self, request):
        """ p2p 회사 추가 [admin token required]"""
        if request.user.username == 'Admin':
            company_name = request.data['company_name']
            homepage_url = request.data['homepage_url']
            nickname = request.data['nickname']
            if len(Company.objects.filter(Q(company_name__icontains=company_name))) != 0:
                return Response(data={'중복된 회사 존재!'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                Company.objects.create(company_name=company_name, homepage_url=homepage_url, nickname=nickname)
            return Response(data={'회사 추가 완료!'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_STRING, description='삭제를 원하는 회사 아이디'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def company_delete(self, request):
        """ 회사 삭제 [admin token required]
        """
        company_id = request.data['company_id']
        if request.user.username == 'Admin':
            company = Company.objects.get(id=company_id)
            company.delete()
            return Response(data={'삭제 완료'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'Admin 페이지 접속 불가능!'}, status=status.HTTP_400_BAD_REQUEST)


class NoticeboardManagementViewSet(viewsets.GenericViewSet):
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
