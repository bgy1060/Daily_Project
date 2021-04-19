from django.db import models


# Create your models here.

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=45, blank=False, null=False)
    homepage_url = models.CharField(max_length=200, blank=False, null=False)
    nickname = models.CharField(max_length=20, blank=False, null=True)

    class Meta:
        db_table = 'company'
