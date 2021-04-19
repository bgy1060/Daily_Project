from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager

from account.models import Account, Deposit_Withdrawal
from users.models import Investing_Balance,Summary_Investing

User = get_user_model()


class CompanyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'account_holder',
            'bank',
            'account_number',
            'deposit'
        )


class CompanyBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investing_Balance
        fields = (
            'total_investment',
            'number_of_investing_products',
            'residual_investment_price',

        )


class CompanyWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit_Withdrawal
        fields = (
            'transaction_amount',
            'remaining_amount',
            'trading_time',

        )

class InvestingiSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    investing_type = serializers.SerializerMethodField()

    class Meta:
        model = Summary_Investing
        fields = (
            'investing_product',
            'investing_price',
            'status',
            'investing_type'
        )

    def get_status(self,obj:Summary_Investing):
        return obj.status.status_meaning

    def get_investing_type(self,obj:Summary_Investing):
        return obj.investing_type.type_meaning

