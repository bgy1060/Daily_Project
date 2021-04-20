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
from .serializers import CompanyAccountSerializer, CompanyBalanceSerializer, CompanyWithdrawalSerializer, \
    InvestingiSerializer
from users.serializers import EmptySerializer
from drf_yasg import openapi
import requests, pickle
from bs4 import BeautifulSoup
from users.models import *
import AES

User = get_user_model()


class DailyViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='계좌 정보를 가져오고 싶은 회사 ID'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def account(self, request):
        """ USER 계좌 정보 가져오기 [token required]"""
        company_id = Company.objects.get(id=int(request.data['company_id']))
        # 세션 시작하기
        session = requests.session()

        try:
            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                session.cookies.update(pickle.load(f))

        except:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
        res = requests.get(url_mypage, cookies=session.cookies)
        res.raise_for_status()

        if '로그인' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "url": "https://www.daily-funding.com:443",
                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

            # 마이페이지에 접근하기
            url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
            res = requests.get(url_mypage, cookies=session.cookies)
            res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        data = soup.select('li.bank_num_info em')

        account_holder = data[0].text
        bank = data[1].text
        account_number = data[2].text
        deposit = int(soup.select_one("ul.info_com span.s_tit em").text.replace('원', '').replace(',', ''))

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

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def balance(self, request):
        """ USER 투자 요약 정보 가져오기 [token required] """
        company_id = Company.objects.get(id=int(request.data['company_id']))

        # 세션 시작하기
        session = requests.session()

        try:
            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                session.cookies.update(pickle.load(f))

        except:

            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {

                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
        res = session.get(url_mypage)
        res.raise_for_status()

        if '로그인' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "url": "https://www.daily-funding.com:443",
                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

            # 마이페이지에 접근하기
            url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
            res = requests.get(url_mypage, cookies=session.cookies)
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
            request.user.investing_balance_set.filter(uid=request.user.id, company_id=company_id).update(
                total_investment=total_investment,
                number_of_investing_products=number_of_investing_products,
                residual_investment_price=residual_investment_price)

        query_set = request.user.investing_balance_set.get(company_id=company_id)
        serializer = CompanyBalanceSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='거래내역 정보를 가져오고 싶은 회사 ID'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def withdrawal(self, request):
        """ USER 거래내역 가져오기 [token required]"""
        company_id = Company.objects.get(id=int(request.data['company_id']))

        # 세션 시작하기
        session = requests.session()

        try:
            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                session.cookies.update(pickle.load(f))

        except:

            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/my_withdraw2.php"
        res = session.get(url_mypage)
        res.raise_for_status()

        if '로그인' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "url": "https://www.daily-funding.com:443",
                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

            # 마이페이지에 접근하기
            url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
            res = requests.get(url_mypage, cookies=session.cookies)
            res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        transaction_amount = soup.select("p.history_change_num")
        remaining_amount = soup.select("p.history_num")
        trading_time = soup.select("p.history_date")

        for i in range(len(trading_time)):
            try:
                request.user.deposit_withdrawal_set.create(transaction_amount=int(transaction_amount[i].
                                                                                  text.replace('원', '').replace(',',
                                                                                                                '')),
                                                           remaining_amount=int(remaining_amount[i].
                                                                                text.replace('원', '').replace(',', '')),
                                                           trading_time=datetime.datetime.strptime(
                                                               str(trading_time[i].text),
                                                               '%Y-%m-%d %H:%M:%S'),
                                                           company_id=company_id, uid=request.user.id)
            except:
                pass

        query_set = request.user.deposit_withdrawal_set.filter(company_id=company_id)
        serializer = CompanyWithdrawalSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='투자내역 정보를 가져오고 싶은 회사 ID'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def investing(self, request):
        """ USER 투자내역 가져오기 [token required]"""
        company_id = Company.objects.get(id=int(request.data['company_id']))

        # 세션 시작하기
        session = requests.session()

        try:
            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'rb') as f:
                session.cookies.update(pickle.load(f))

        except:

            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

        # 마이페이지에 접근하기
        url_mypage = "https://www.daily-funding.com/mypage/investitems.php"
        res = session.get(url_mypage)
        res.raise_for_status()

        if '로그인' in res.text:
            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                "url": "https://www.daily-funding.com:443",
                "mb_id": USER,  # 아이디 지정
                "mb_password": PASS  # 비밀번호 지정
            }

            url_login = "https://www.daily-funding.com/bbs/login_check.php"
            res = session.post(url_login, data=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(session.cookies, f)

            # 마이페이지에 접근하기
            url_mypage = "https://www.daily-funding.com/mypage/my_info.php"
            res = requests.get(url_mypage, cookies=session.cookies)
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
