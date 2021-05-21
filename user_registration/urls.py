"""user_registration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers

from _8percent.views import _8PercentViewSet
from _90days.views import _90DaysViewSet
from bf_fund.views import BFViewSet
from cocktail_funding.views import CocktailViewSet
from daon_funding.views import DaonViewSet
from fun_funding.views import FunViewSet
from hello_funding.views import HelloViewSet
from honest_fund.views import HonestViewSet
from leadingplus_funding.views import LeadingPlusViewSet
from lendit.views import LenditViewSet
from loanpoint.views import LoanPointViewSet
from miracle_funding.views import MiracleViewSet
from mosaic_funding.views import MosaicViewSet
from niceabc.views import NiceabcViewSet
from people_fund.views import PeopleViewSet
from profit.views import ProfitViewSet
from tera_funding.views import TeraViewSet
from theasset.views import TheassetViewSet
from together_funding.views import TogetherViewSet
from users.views import *
from daily_funding.views import *
from notice_board.views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from v_funding.views import VFundingViewSet


schema_view = get_schema_view(
    openapi.Info(title="Snippets API",
                 default_version='v1',
                 description="Test description",
                 terms_of_service="https://www.google.com/policies/terms/",
                 contact=openapi.Contact(email="contact@snippets.local"),
                 license=openapi.License(name="BSD License"),
                 ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter(trailing_slash=False)
router.register('api/auth', AuthViewSet, basename='auth')
router.register('api/register', RegisterViewSet, basename='register')
router.register('api/daily', DailyViewSet, basename='daily_funding')
router.register('api/notice', NoticeBoardViewSet, basename='notice_board')
router.register('api/join', CodeViewSet, basename='join_code')
router.register('api/tera', TeraViewSet, basename='tera_funding')
router.register('api/people', PeopleViewSet, basename='people_fund')
router.register('api/hello', HelloViewSet, basename='hello_funding')
router.register('api/honest', HonestViewSet, basename='honest_fund')
router.register('api/profit', ProfitViewSet, basename='profit')
router.register('api/lendit', LenditViewSet, basename='lendit')
router.register('api/theasset', TheassetViewSet, basename='theasset')
router.register('api/loanpoint', LoanPointViewSet, basename='loanpoint')
router.register('api/niceabc', NiceabcViewSet, basename='niceabc')
router.register('api/v', VFundingViewSet, basename='v_funding')
router.register('api/bf', BFViewSet, basename='bf_fund')
router.register('api/miracle', MiracleViewSet, basename='miracle_funding')
router.register('api/mosaic', MosaicViewSet, basename='mosaic_funding')
router.register('api/fun', FunViewSet, basename='fun_funding')
router.register('api/8percent', _8PercentViewSet, basename='_8percent')
router.register('api/90days', _90DaysViewSet, basename='_90days')
router.register('api/together', TogetherViewSet, basename='together_funding')
router.register('api/cocktail', CocktailViewSet, basename='cocktail_funding')
router.register('api/daon', DaonViewSet, basename='daon_funding')
router.register('api/leadingplus', LeadingPlusViewSet, basename='leadingplus_funding')


urlpatterns = router.urls + [
    path('admin/', admin.site.urls),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


]
