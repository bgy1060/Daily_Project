from django.contrib import admin
from notice_board.models import *
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'category_name']
    list_display_links = ['category_id', 'category_name']


@admin.register(NoticeBoard)
class NoticeBoardAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'title', 'date', 'views', 'like', 'dislike', 'uid_id']
    list_display_links = ['post_id', 'title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'comment_content', 'date', 'like', 'dislike']
    list_display_links = ['comment_id', 'comment_content']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'answer', 'view', 'order']
    list_display_links = ['id', 'question', 'answer']


@admin.register(Point_action)
class PointActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'point_value', 'limit_number_of_day']
    list_display_links = ['id', 'action']


@admin.register(Point_List)
class PointListAdmin(admin.ModelAdmin):
    list_display = ['id', 'action_id', 'uid', 'point', 'total_point', 'date', 'detail_action']
    list_display_links = ['id', 'action_id']