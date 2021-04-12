from django.db import models
from company.models import *
# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, default="")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True,
                                  null=False)
    last_name = models.CharField(max_length=255, blank=True,
                                 null=False)

    withdrawal_status = models.BooleanField(default=False)
    withdrawal_date = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"

    class Meta:
        db_table = 'user'


class Register(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    username = models.CharField(max_length=500, blank=False, null=False)
    user_password = models.CharField(max_length=500, blank=False, null=False)

    class Meta:
        db_table = 'register'
        unique_together = ['company_id', 'uid']


class Investing_Status(models.Model):
    status_code = models.CharField(max_length=45, primary_key=True)
    status_meaning = models.CharField(max_length=45)

    class Meta:
        db_table = 'investing_status'


class Investing_Type(models.Model):
    type_code = models.CharField(max_length=45, primary_key=True)
    type_meaning = models.CharField(max_length=45)

    class Meta:
        db_table = 'investing_type'


class Summary_Investing(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    investing_product = models.CharField(max_length=45)
    investing_price = models.PositiveIntegerField()
    status = models.ForeignKey(Investing_Status, on_delete=models.CASCADE)
    investing_type = models.ForeignKey(Investing_Type, on_delete=models.CASCADE)

    class Meta:
        db_table = 'summary_investing'
        unique_together = ['company_id', 'investing_product', 'investing_price']


class Investing_Balance(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    total_investment = models.DecimalField(max_digits=13, decimal_places=0)
    number_of_investing_products = models.IntegerField()
    residual_investment_price = models.PositiveIntegerField()

    class Meta:
        db_table = 'investing_balance'
        unique_together = ['company_id', 'uid']


