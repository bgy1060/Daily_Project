# Create your views here.
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
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

from selenium import webdriver
import time

User = get_user_model()


class _90DaysViewSet(viewsets.GenericViewSet):
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
        driver = webdriver.Chrome("C:/Users/daily-funding/Desktop/chromedriver")

        if request.data['refresh'] == 0:
            query_set = request.user.account_set.get(company_id=company_id)
            serializer = CompanyAccountSerializer(query_set)
            return JsonResponse(serializer.data, safe=False)
            return Response(status=status.HTTP_200_OK)

        driver.get("https://90days.kr/login?u=/k2/")

        username = request.user.register_set.get(company_id=company_id).username.strip()
        password = request.user.register_set.get(company_id=company_id).user_password.strip()

        decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
        decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

        USER = decrypted_username.decode()
        PASS = decrypted_password.decode()

        email = driver.find_element_by_css_selector("input#login_id")
        email.send_keys(USER)

        pwd = driver.find_element_by_css_selector("input#login_passwd")
        pwd.send_keys(PASS)

        login_btn = driver.find_element_by_css_selector("input#login_bt1")
        login_btn.send_keys('\n')

        time.sleep(1)

        driver.get('https://90days.kr/k2/member/my-page')
        driver.get('https://90days.kr/k2/member/portfolio')

        time.sleep(0.5)

        account_holder = driver.find_element_by_css_selector("h4.h4-default.portfolio__profile__name").text.replace(
            "님의 예치금", "")
        bank, account_number = driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/p[2]').text.split(" ")
        deposit = driver.find_element_by_css_selector("h2.h2-default.portfolio__profile__deposit").text.replace("원", "")

        try:
            request.user.account_set.create(bank=bank, account_holder=account_holder, account_number=account_number,
                                            deposit=deposit, company_id=company_id, uid=request.user.id)


        except:
            request.user.account_set.filter(uid=request.user.id, company_id=company_id).update(bank=bank,
                                                                                               account_number=account_number,
                                                                                               deposit=deposit)
        driver.close()
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
        driver = webdriver.Chrome("C:/Users/daily-funding/Desktop/chromedriver")

        # 세션 시작하기
        session = requests.session()

        if request.data['refresh'] == 0:
            query_set = request.user.investing_balance_set.get(company_id=company_id)
            serializer = CompanyBalanceSerializer(query_set)
            return JsonResponse(serializer.data, safe=False)
            return Response(status=status.HTTP_200_OK)

        driver.get("https://90days.kr/login?u=/k2/")

        username = request.user.register_set.get(company_id=company_id).username.strip()
        password = request.user.register_set.get(company_id=company_id).user_password.strip()

        decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
        decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

        USER = decrypted_username.decode()
        PASS = decrypted_password.decode()

        email = driver.find_element_by_css_selector("input#login_id")
        email.send_keys(USER)

        pwd = driver.find_element_by_css_selector("input#login_passwd")
        pwd.send_keys(PASS)

        login_btn = driver.find_element_by_css_selector("input#login_bt1")
        login_btn.send_keys('\n')

        time.sleep(1)

        driver.get('https://90days.kr/k2/member/my-page')
        driver.get('https://90days.kr/k2/member/portfolio')

        time.sleep(1)

        driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/ul/li[1]/button').click()

        time.sleep(1)

        total_investment = driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div/div[2]/div/div[1]/div[2]/button[3]/div/h3').text.replace("원", "")
        number_of_investing_products = driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/div[2]/p[1]/span[2]').text.replace("건",
                                                                                                                   "")
        residual_investment_price = int(driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div/div[2]/div/div[1]/div[2]/button[4]/div/h3').text.replace("원", "")) - \
                                    int(driver.find_element_by_css_selector(
                                        "h2.h2-default.portfolio__profile__deposit").text.replace("원", ""))

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

        driver.close()
        query_set = request.user.investing_balance_set.get(company_id=company_id)
        serializer = CompanyBalanceSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)
