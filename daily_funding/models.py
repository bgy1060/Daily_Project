from django.db import models
from users.models import *
from company.models import *


class Cookie(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    cookie_value = models.CharField(max_length=100, default="")

    class Meta:
        db_table = 'cookie'
        unique_together = ['company_id', 'uid']



