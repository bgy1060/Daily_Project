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

import my_settings
from users.serializers import EmptySerializer
from drf_yasg import openapi
import requests, pickle
from bs4 import BeautifulSoup
from users.models import *
import AES
import re

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

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def account(self, request):
        """ USER 계좌 정보 가져오기 [token required]"""

        company_id = Company.objects.get(id=int(request.data['company_id']))
        # 세션 시작하기
        session = requests.session()

        try:
            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(company_id.id) + '_cookie.txt', 'rb') as f:
                auth = pickle.load(f)

        except:
            # 테라 펀딩 사이트 접근
            company_url = "https://www.terafunding.com/"
            res = requests.get(company_url)
            res.raise_for_status()

            # 로그인에 필요한 정보 가져오기
            script = re.findall('<script type="text/javascript" src="\S+</script>', res.text)
            src = re.findall('_nuxt/\S+.js', script[-1])

            url = company_url + src[0]
            res = requests.get(url)

            data = re.findall('client_id:"\S+",client_secret:"\S+",grant_type:"\S+",scope:\S+"}', res.text)
            data = data[0].split(',')

            client_id = data[0].replace('client_id:', "").replace('"', "")
            client_secret = data[1].replace('client_secret:', "").replace('"', "")
            grant_type = data[2].replace('grant_type:', "").replace('"', "")
            scope = data[3].replace('scope:', "").replace('"', "").replace("}", "")

            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                'username': USER,
                'password': PASS,
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': grant_type,
                'scope': scope,
            }

            url_login = "https://api.terafunding.com/oauth/signin"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/'+str(request.user.id)+'_'+str(company_id.id)+'_cookie.txt', 'wb') as f:
                pickle.dump(res.json()['token_type']+" " + res.json()['access_token'], f)


        request_headers = {
                'authorization': auth
        }

        account_api = "https://api.terafunding.com/user/v1/investor"
        res = session.get(account_api, headers=request_headers)

        if 'errorName' in res.text:
            # 테라 펀딩 사이트 접근
            company_url = "https://www.terafunding.com/"
            res = requests.get(company_url)
            res.raise_for_status()

            # 로그인에 필요한 정보 가져오기
            script = re.findall('<script type="text/javascript" src="\S+</script>', res.text)
            src = re.findall('_nuxt/\S+.js', script[-1])

            url = company_url + src[0]
            res = requests.get(url)

            data = re.findall('client_id:"\S+",client_secret:"\S+",grant_type:"\S+",scope:\S+"}', res.text)
            data = data[0].split(',')

            client_id = data[0].replace('client_id:', "").replace('"', "")
            client_secret = data[1].replace('client_secret:', "").replace('"', "")
            grant_type = data[2].replace('grant_type:', "").replace('"', "")
            scope = data[3].replace('scope:', "").replace('"', "").replace("}", "")

            username = request.user.register_set.get(company_id=company_id).username.strip()
            password = request.user.register_set.get(company_id=company_id).user_password.strip()

            decrypted_username = AES.AESCipher(bytes(my_settings.key)).decrypt(username)
            decrypted_password = AES.AESCipher(bytes(my_settings.key)).decrypt(password)

            USER = decrypted_username
            PASS = decrypted_password

            login_info = {
                'username': USER,
                'password': PASS,
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': grant_type,
                'scope': scope,
            }

            url_login = "https://api.terafunding.com/oauth/signin"
            res = session.post(url_login, json=login_info)
            res.raise_for_status()  # 오류가 발생하면 예외가 발생합니다.

            with open('C:/Users/daily-funding/Desktop/cookie/' + str(request.user.id) + '_' + str(
                    company_id.id) + '_cookie.txt', 'wb') as f:
                pickle.dump(res.json()['token_type'] + " " + res.json()['access_token'], f)

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
            request.user.account_set.update(bank=bank, account_number=account_number, deposit=deposit)

        query_set = request.user.account_set.get(company_id=company_id)
        serializer = CompanyAccountSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_201_CREATED)
