# Create your views here.
import requests
from django.db import models
from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import datetime

import base64
from Crypto import Random
from Crypto.Cipher import AES
import my_settings
from . import serializers
from .serializers import CompanyAccountSerializer, CompanyBalanceSerializer, CompanyWithdrawalSerializer, InvestingiSerializer

User = get_user_model()

from company.models import Company

import requests
from bs4 import BeautifulSoup
from users.models import *

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


class DailyViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def account(self, request):
        company_id = request.data['company_id']

        username = request.user.register_set.get(company_id=company_id).username.strip()
        password = request.user.register_set.get(company_id=company_id).user_password.strip()

        decrypted_username = AESCipher(bytes(my_settings.key)).decrypt(username)
        decrypted_password = AESCipher(bytes(my_settings.key)).decrypt(password)

        USER = decrypted_username
        PASS = decrypted_password

        login_info = {
            "action": "is_login_check",
            "return_url": "https://www.daily-funding.com/",
            "mb_id": USER,  # 아이디 지정
            "mb_password": PASS  # 비밀번호 지정
        }

        # 세션 시작하기
        session = requests.session()

        url_login = "https://www.daily-funding.com/bbs/login_check.php"
        res = session.post(url_login, data=login_info)
        res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
        res = session.get(url_mypage)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        data = soup.select('li.bank_num_info em')

        account_holder = data[0].text
        bank = data[1].text
        account_number = data[2].text
        deposit = int(soup.select_one("ul.info_com span.s_tit em").text.replace('원', '').replace(',', ''))
        print(deposit)

        try:
            request.user.account_set.create(bank=bank, account_holder=account_holder, account_number=account_number,
                                            deposit=deposit, company_id=company_id, uid=request.user.id)


        except:
            request.user.account_set.update(bank=bank, account_number=account_number, deposit=deposit)

        query_set = request.user.account_set.get(company_id=company_id)
        serializer = CompanyAccountSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def balance(self, request):
        company_id = request.data['company_id']

        username = request.user.register_set.get(company_id=company_id).username.strip()
        password = request.user.register_set.get(company_id=company_id).user_password.strip()

        decrypted_username = AESCipher(bytes(my_settings.key)).decrypt(username)
        decrypted_password = AESCipher(bytes(my_settings.key)).decrypt(password)

        USER = decrypted_username
        PASS = decrypted_password

        login_info = {
            "action": "is_login_check",
            "return_url": "https://www.daily-funding.com/",
            "mb_id": USER,  # 아이디 지정
            "mb_password": PASS  # 비밀번호 지정
        }

        # 세션 시작하기
        session = requests.session()

        url_login = "https://www.daily-funding.com/bbs/login_check.php"
        res = session.post(url_login, data=login_info)
        res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
        res = session.get(url_mypage)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        total_investment = soup.select_one("div#totalAmount").text.strip().replace('원', '').replace(',', '')
        number_of_investing_products = soup.select_one("div#investCount").text.strip().replace('건', '')
        residual_investment_price = soup.select_one("p.tit_result").text.strip().replace('원', '').replace(',', '')

        try:
            request.user.investing_balance_set.create(total_investment=total_investment,
                                                      number_of_investing_products=number_of_investing_products,
                                                      residual_investment_price=residual_investment_price,
                                                      company_id=company_id, uid=request.user.id)
        except:
            request.user.investing_balance_set.update(total_investment=total_investment,
                                                      number_of_investing_products=number_of_investing_products,
                                                      residual_investment_price=residual_investment_price)

        query_set = request.user.investing_balance_set.get(company_id=company_id)
        serializer = CompanyBalanceSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def withdrawal(self, request):
        company_id = request.data['company_id']

        username = request.user.register_set.get(company_id=company_id).username.strip()
        password = request.user.register_set.get(company_id=company_id).user_password.strip()

        decrypted_username = AESCipher(bytes(my_settings.key)).decrypt(username)
        decrypted_password = AESCipher(bytes(my_settings.key)).decrypt(password)

        USER = decrypted_username
        PASS = decrypted_password

        login_info = {
            "action": "is_login_check",
            "return_url": "https://www.daily-funding.com/",
            "mb_id": USER,  # 아이디 지정
            "mb_password": PASS  # 비밀번호 지정
        }

        # 세션 시작하기
        session = requests.session()

        url_login = "https://www.daily-funding.com/bbs/login_check.php"
        res = session.post(url_login, data=login_info)
        res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/my_withdraw2.php"
        res = session.get(url_mypage)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        transaction_amount = soup.select("p.history_change_num")
        remaining_amount = soup.select("p.history_num")
        trading_time = soup.select("p.history_date")

        for i in range(len(trading_time)):
            try:
                request.user.deposit_withdrawal_set.create(transaction_amount=int(transaction_amount[i].
                                                                              text.replace('원', '').replace(',', '')),
                                                       remaining_amount=int(remaining_amount[i].
                                                                            text.replace('원', '').replace(',', '')),
                                                       trading_time=datetime.datetime.strptime(str(trading_time[i].text),
                                                                                               '%Y-%m-%d %H:%M:%S'),
                                                       company_id=company_id, uid=request.user.id)
                print("insert")
            except:
                print('pass')
                pass

        query_set = request.user.deposit_withdrawal_set.filter(company_id=company_id)
        serializer = CompanyWithdrawalSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def investing(self, request):
        company_id = request.data['company_id']

        username = request.user.register_set.get(company_id=company_id).username.strip()
        password = request.user.register_set.get(company_id=company_id).user_password.strip()

        decrypted_username = AESCipher(bytes(my_settings.key)).decrypt(username)
        decrypted_password = AESCipher(bytes(my_settings.key)).decrypt(password)

        USER = decrypted_username
        PASS = decrypted_password

        login_info = {
            "action": "is_login_check",
            "return_url": "https://www.daily-funding.com/",
            "mb_id": USER,  # 아이디 지정
            "mb_password": PASS  # 비밀번호 지정
        }

        # 세션 시작하기
        session = requests.session()

        url_login = "https://www.daily-funding.com/bbs/login_check.php"
        res = session.post(url_login, data=login_info)
        res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/investitems.php"
        res = session.get(url_mypage)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        invest = soup.select("div.invest_item a")

        for i in range(len(invest)):
            idx, price, i_idx = invest[0].attrs["href"].split(',')

            idx = idx.replace("javascript:open_de(", '').strip()
            price = price.strip()
            i_idx = i_idx.replace(')', '').strip()

            detail_invest_url = 'https://www.daily-funding.com/mypage/ajax.linvestment.php?idx=' + idx + '&price=' + price + '&i_idx=' + i_idx
            res = session.get(detail_invest_url)
            res.raise_for_status()

            soup = BeautifulSoup(res.text, "html.parser")

            investing_product = soup.select_one('div.inv_detail_wrap>h2>a').text
            investing_price = int(soup.select_one('div.txtmid3 span').text.replace('만원', '') + '0000')
            status = Investing_Status.objects.get(status_meaning=soup.select('div.txtmid4 span')[1].text)
            investing_type = Investing_Type.objects.get(type_meaning=soup.select_one('div span.product_state').text)

            try:
                request.user.summary_investing_set.create(investing_product=investing_product,
                                                          investing_price=investing_price,
                                                          status=status,
                                                          investing_type=investing_type,
                                                          company_id=company_id, uid=request.user.id)
            except:
                pass

            query_set = request.user.summary_investing_set.filter(company_id=company_id)
            serializer = InvestingiSerializer(query_set, many=True)
            return JsonResponse(serializer.data, safe=False)
            return Response(status=status.HTTP_201_CREATED)