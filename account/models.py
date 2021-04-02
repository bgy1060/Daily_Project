from django.db import models
from users.models import *
from company.models import *


# Create your models here.

class Account(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    account_holder = models.CharField(max_length=45)
    bank = models.CharField(max_length=30)
    account_holder = models.CharField(max_length=50)
    deposit = models.DecimalField(max_digits=13, decimal_places=0)

    class Meta:
        db_table = 'account'


class Deposit_Withdrawal(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    transaction_amount = models.DecimalField(max_digits=13, decimal_places=0)
    remaining_amount = models.DecimalField(max_digits=13, decimal_places=0)
    trading_time = models.DateTimeField(default='')

    class Meta:
        db_table = 'deposit_withdrawal'