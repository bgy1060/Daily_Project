from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

import my_settings
from users.serializers import EmptySerializer
from drf_yasg import openapi
import requests, pickle
from users.models import *
import AES
import re
from tera_funding.login_info import login

from daily_funding.serializers import *

User = get_user_model()


class TeraViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = EmptySerializer
    serializer_classes = {

    }

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
            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
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
                'username': USER.decode(),
                'password': PASS.decode(),
                'client_id': login()[0],
                'client_secret': login()[1],
                'grant_type': login()[2],
                'scope': login()[3],
            }

            url_login = "https://api.terafunding.com/oauth/signin"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(res.json()['token_type'] + " " + res.json()['access_token'], f)

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

        request_headers = {
            'authorization': auth
        }

        account_api = "https://api.terafunding.com/user/v1/investor"
        res = session.get(account_api, headers=request_headers)

        if 'Access token expired' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                'username': USER.decode(),
                'password': PASS.decode(),
                'client_id': login()[0],
                'client_secret': login()[1],
                'grant_type': login()[2],
                'scope': login()[3],
            }

            url_login = "https://api.terafunding.com/oauth/signin"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(res.json()['token_type'] + " " + res.json()['access_token'], f)

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

            request_headers = {
                'authorization': auth
            }

            account_api = "https://api.terafunding.com/user/v1/investor"
            res = session.get(account_api, headers=request_headers)

        account_holder = res.json()['value']['name'].strip()
        bank = res.json()['value']['vbankName'].strip()
        account_number = res.json()['value']['vaccountNumber'].strip()
        deposit = res.json()['value']['balance']

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
            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
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
                'username': USER.decode(),
                'password': PASS.decode(),
                'client_id': login()[0],
                'client_secret': login()[1],
                'grant_type': login()[2],
                'scope': login()[3],
            }

            url_login = "https://api.terafunding.com/oauth/signin"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(res.json()['token_type'] + " " + res.json()['access_token'], f)

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

        request_headers = {
            'authorization': auth
        }

        balance_api = "https://api.terafunding.com/user/v1/dashboard"
        res = session.get(balance_api, headers=request_headers)

        if 'Access token expired' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                'username': USER.decode(),
                'password': PASS.decode(),
                'client_id': login()[0],
                'client_secret': login()[1],
                'grant_type': login()[2],
                'scope': login()[3],
            }

            url_login = "https://api.terafunding.com/oauth/signin"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(res.json()['token_type'] + " " + res.json()['access_token'], f)

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

            request_headers = {
                'authorization': auth
            }

            balance_api = "https://api.terafunding.com/user/v1/dashboard"
            res = session.get(balance_api, headers=request_headers)

        total_investment = res.json()['investProfit']['totalAmt']
        residual_investment_price = res.json()['investProfit']['grandTotalPreAmt']

        num_product_url = "https://api.terafunding.com/funding/v1/user-invests/summary"
        res = session.get(num_product_url, headers=request_headers)
        number_of_investing_products = res.json()['map']['CREATED']['count']

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
