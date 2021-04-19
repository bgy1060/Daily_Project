from django.contrib import admin
from company.models import *
# Register your models here.


@admin.register(Company)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'company_name', 'homepage_url', 'nickname']
    list_display_links = ['id', 'company_name', 'homepage_url', 'nickname']


