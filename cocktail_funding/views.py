from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from account.models import Bank
import datetime

import my_settings
from daily_funding.serializers import CompanyAccountSerializer, CompanyBalanceSerializer, CompanyWithdrawalSerializer, \
    InvestingiSerializer
from users.serializers import EmptySerializer
from drf_yasg import openapi
import requests, pickle
from bs4 import BeautifulSoup
from users.models import *
import AES

User = get_user_model()


class CocktailViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, description='로그인 아이디'),
            'pwd': openapi.Schema(type=openapi.TYPE_STRING, description='로그인 비밀번호'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def is_valid(self, request):
        """ 사용자가 입력한 로그인 정보가 유효한 값인지 확인 [token required]"""

        # 세션 시작하기
        session = requests.session()

        USER = request.data['id']
        PASS = request.data['pwd']

        login_info = {
            "email": USER,  # 아이디 지정
            "password": PASS  # 비밀번호 지정
        }
        try:
            url_login = "https://api.cocktailfunding.com/api/v2/auth/login"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.
            return Response(data={"valid!"}, status=status.HTTP_200_OK)
        except:
            return Response(data={"invalid!"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='계좌 정보를 가져오고 싶은 회사 ID'),
            'refresh': openapi.Schema(type=openapi.TYPE_INTEGER, description='값이 1이면 크롤링 해서 데이터 가져오기, 값이 0이면 DB에 저장되어 '
                                                                             '있는 값 가져오기'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def account(self, request):
        """ USER 계좌 정보 가져오기 [token required]"""
        company_id = Company.objects.get(id=int(request.data['company_id']))
        # 세션 시작하기
        session = requests.session()

        if request.data['refresh'] == 0:
            query_set = request.user.account_set.get(company_id=company_id)
            serializer = CompanyAccountSerializer(query_set)
            return JsonResponse(serializer.data, safe=False)
            return Response(status=status.HTTP_200_OK)

        try:
            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

        except:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "email": USER.decode(),  # 아이디 지정
                "password": PASS.decode()  # 비밀번호 지정
            }

            url_login = "https://api.cocktailfunding.com/api/v2/auth/login"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump("Bearer " + res.json()['body']['token'], f)

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

        request_headers = {
            'authorization': auth
        }

        account_api = "https://api.cocktailfunding.com/api/v2/mypage/personal"
        res = session.get(account_api, headers=request_headers)

        if 'InvalidJwtToken' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "email": USER.decode(),  # 아이디 지정
                "password": PASS.decode()  # 비밀번호 지정
            }

            url_login = "https://api.cocktailfunding.com/api/v2/auth/login"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump("Bearer " + res.json()['body']['token'], f)

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

            request_headers = {
                'authorization': auth
            }

            account_api = "https://api.cocktailfunding.com/api/v2/mypage/personal"
            res = session.get(account_api, headers=request_headers)

        account_holder = res.json()['body']['fund_account_name']
        account_number = res.json()['body']['fund_account']
        deposit = res.json()['body']['balance']

        bank_code = res.json()['body']['fund_account_bank']
        bank = Bank.objects.get(code=bank_code).bank

        try:
            request.user.account_set.create(bank=bank, account_holder=account_holder, account_number=account_number,
                                            deposit=deposit, company_id=company_id, uid=request.user.id)


        except:
            request.user.account_set.filter(uid=request.user.id, company_id=company_id).update(bank=bank,
                                                                                               account_number=account_number,
                                                                                               deposit=deposit)

        query_set = request.user.account_set.get(company_id=company_id)
        serializer = CompanyAccountSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='투자 요약 정보를 가져오고 싶은 회사 ID'),
            'refresh': openapi.Schema(type=openapi.TYPE_INTEGER, description='값이 1이면 크롤링 해서 데이터 가져오기, 값이 0이면 DB에 저장되어 '
                                                                             '있는 값 가져오기'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def balance(self, request):
        """ USER 투자 요약 정보 가져오기 [token required] """
        company_id = Company.objects.get(id=int(request.data['company_id']))

        # 세션 시작하기
        session = requests.session()

        if request.data['refresh'] == 0:
            query_set = request.user.investing_balance_set.get(company_id=company_id)
            serializer = CompanyBalanceSerializer(query_set)
            return JsonResponse(serializer.data, safe=False)
            return Response(status=status.HTTP_200_OK)

        try:
            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

        except:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "email": USER.decode(),  # 아이디 지정
                "password": PASS.decode()  # 비밀번호 지정
            }

            url_login = "https://api.cocktailfunding.com/api/v2/auth/login"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump("Bearer " + res.json()['body']['token'], f)

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

        request_headers = {
            'authorization': auth
        }

        account_api = "https://api.cocktailfunding.com/api/v2/mypage/personal"
        res = session.get(account_api, headers=request_headers)

        if 'InvalidJwtToken' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "email": USER.decode(),  # 아이디 지정
                "password": PASS.decode()  # 비밀번호 지정
            }

            url_login = "https://api.cocktailfunding.com/api/v2/auth/login"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump("Bearer " + res.json()['body']['token'], f)

            with open('cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

            request_headers = {
                'authorization': auth
            }

            account_api = "https://api.cocktailfunding.com/api/v2/mypage/personal"
            res = session.get(account_api, headers=request_headers)

        collateral_sum = res.json()['body']['currentInvest']['collateral_sum']
        non_collateral_sum = res.json()['body']['currentInvest']['non_collateral_sum']

        if collateral_sum is None:
            collateral_sum = 0

        if non_collateral_sum is None:
            non_collateral_sum = 0

        total_investment = collateral_sum+non_collateral_sum
        number_of_investing_products = res.json()['body']['currentInvest']['invest_count']

        residual_url = "https://api.cocktailfunding.com/api/v2/mypage/betadashboard"
        res = session.get(residual_url, headers=request_headers)
        expected_return_interest = res.json()['body']['ExpectedReturnAmount']['expected_return_interest']

        if expected_return_interest is None:
            expected_return_interest = 0

        residual_investment_price = expected_return_interest

        try:
            request.user.investing_balance_set.create(total_investment=total_investment,
                                                      number_of_investing_products=number_of_investing_products,
                                                      residual_investment_price=residual_investment_price,
                                                      company_id=company_id, uid=request.user.id)
        except:
            request.user.investing_balance_set.filter(uid=request.user.id, company_id=company_id).update(
                total_investment=total_investment,
                number_of_investing_products=number_of_investing_products,
                residual_investment_price=residual_investment_price)

        query_set = request.user.investing_balance_set.get(company_id=company_id)
        serializer = CompanyBalanceSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)
