from django.contrib import admin
from admin_page.models import *
# Register your models here.


@admin.register(AdminCategory)
class AdminCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'category_name', 'parent_category']
    list_display_links = ['category_id', 'category_name']
