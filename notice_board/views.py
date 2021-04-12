from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from . import serializers
from .models import *
from .serializers import PostListSerializer, DetailPostSerializer, CommentListSerializer, CategoryListSerializer, FAQListSerializer
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


class NoticeBoardViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {

    }

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def write_post(self, request):
        data = request.data
        print(data)
        request.user.noticeboard_set.create(title=data['title'], content=data['content'], date=timezone.now(),
                                            category_id=request.data['category_id'], uid=request.user.id)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def update_post(self, request):
        data = request.data
        post_id = request.data['post_id']
        post = request.user.noticeboard_set.get(post_id=post_id)
        post.title = data['title']
        post.content = data['content']
        post.save()
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def delete_post(self, request):
        post_id = request.data['post_id']
        post = request.user.noticeboard_set.get(post_id=post_id)
        post.delete()
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def detail_post(self, request):
        post_id = request.data['post_id']
        query_set = NoticeBoard.objects.get(post_id=post_id)
        serializer = DetailPostSerializer(query_set)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def update_view(self, request):
        post_id = request.data['post_id']
        post = NoticeBoard.objects.get(post_id=post_id)
        post.views = post.views + 1
        post.save()
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['GET', ], detail=False)
    def post_view(self, request):
        post_id = request.data['post_id']
        post_view = NoticeBoard.objects.get(post_id=post_id).views
        return Response(data=post_view, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['GET', ], detail=False)
    def category_list(self, request):
        query_set = Category.objects.all()
        serializer = CategoryListSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def post_list(self, request):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = request.data['page_size']
            category_id = request.data['category_id']
            query_set = NoticeBoard.objects.filter(category_id=category_id).order_by('-post_id')
            result_page = paginator.paginate_queryset(query_set, request)
            serializer = PostListSerializer(result_page, many=True)

        except:
            paginator = PageNumberPagination()
            paginator.page_size = request.data['page_size']
            query_set = NoticeBoard.objects.all().order_by('-post_id')
            result_page = paginator.paginate_queryset(query_set, request)
            serializer = PostListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def comment_list(self, request):
        post_id = request.data['post_id']
        try:
            parent_comment = request.data['parent_comment']
            query_set = Comment.objects.filter(post_id=post_id).filter(parent_comment=parent_comment)
            serializer = CommentListSerializer(query_set, many=True)
        except:
            query_set = Comment.objects.filter(post_id=post_id).filter(parent_comment__isnull=True)
            serializer = CommentListSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def write_comment(self, request):
        data = request.data
        post_id = NoticeBoard.objects.get(post_id=int(request.data['post_id']))
        try:
            parent_comment = Comment.objects.get(comment_id=int(request.data['parent_comment']))
            request.user.comment_set.create(comment_content=data['comment_content'], date=timezone.now(),
                                            post_id=post_id, uid=request.user.id, parent_comment=parent_comment)
        except:
            request.user.comment_set.create(comment_content=data['comment_content'], date=timezone.now(),
                                            post_id=post_id, uid=request.user.id)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def update_comment(self, request):
        data = request.data
        comment_id = request.data['comment_id']
        comment = request.user.comment_set.get(comment_id=comment_id)
        comment.comment_content = data['comment_content']
        comment.save()
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def delete_comment(self, request):
        comment_id = request.data['comment_id']
        comment = request.user.comment_set.get(comment_id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_post_like(self, request):
        try:
            post_id = NoticeBoard.objects.get(post_id=int(request.data['post_id']))
        except:
            message = {"The post has already been deleted and does not exist."}
            return Response(data=message, status=status.HTTP_200_OK)
        like_dislike = request.data['like_dislike']
        if like_dislike == 1:
            try:
                request.user.noticeboardlike_set.create(like_dislike=like_dislike, post_id=post_id, uid=request.user.id)
                post = NoticeBoard.objects.get(post_id=request.data['post_id'])
                post.like = NoticeBoard.objects.get(post_id=request.data['post_id']).like + 1
                post.save()
                data = post.like
            except:
                message = {"You have already liked it"}
                return Response(data=message, status=status.HTTP_200_OK)

        elif like_dislike == 0:
            try:
                request.user.noticeboardlike_set.create(like_dislike=like_dislike, post_id=post_id, uid=request.user.id)
                post = NoticeBoard.objects.get(post_id=request.data['post_id'])
                post.dislike = NoticeBoard.objects.get(post_id=request.data['post_id']).dislike + 1
                post.save()
                data=post.dislike
            except:
                message = {"You have already disliked it"}
                return Response(data=message, status=status.HTTP_200_OK)
        else:
            message = {"Please enter according to the format"}
            return Response(data=message, status=status.HTTP_200_OK)

        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def cancel_post_like(self, request):
        like_dislike = request.data['like_dislike']
        if like_dislike == 1:
            post_id = request.data['post_id']
            try:
                like = request.user.noticeboardlike_set.get(post_id=post_id, uid=request.user.id)
                like.delete()
            except:
                message = {"Like cannot be less than 0"}
                return Response(data=message, status=status.HTTP_200_OK)

            post = NoticeBoard.objects.get(post_id=request.data['post_id'])
            post.like = NoticeBoard.objects.get(post_id=request.data['post_id']).like - 1
            post.save()
            message = post.like
        elif like_dislike == 0:
            post_id = request.data['post_id']
            try:
                dislike = request.user.noticeboardlike_set.get(post_id=post_id, uid=request.user.id)
                dislike.delete()
            except:
                message = {"Dislike cannot be less than 0"}
                return Response(data=message, status=status.HTTP_200_OK)

            post = NoticeBoard.objects.get(post_id=request.data['post_id'])
            post.dislike = NoticeBoard.objects.get(post_id=request.data['post_id']).dislike - 1
            post.save()
            message = post.dislike
        else:
            message = {"Please enter according to the format"}
            return Response(data=message, status=status.HTTP_200_OK)

        return Response(data=message, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_comment_like(self, request):
        try:
            comment_id = Comment.objects.get(comment_id=int(request.data['comment_id']))
        except:
            message = {"The post has already been deleted and does not exist."}
            return Response(data=message, status=status.HTTP_200_OK)
        like_dislike = request.data['like_dislike']
        if like_dislike == 1:
            try:
                request.user.commentlike_set.create(like_dislike=like_dislike, comment_id=comment_id, uid=request.user.id)
                comment = Comment.objects.get(comment_id=request.data['comment_id'])
                comment.like = Comment.objects.get(comment_id=request.data['comment_id']).like + 1
                comment.save()
                data = comment.like
            except:
                message = {"You have already liked it"}
                return Response(data=message, status=status.HTTP_200_OK)

        elif like_dislike == 0:
            try:
                request.user.commentlike_set.create(like_dislike=like_dislike, comment_id=comment_id, uid=request.user.id)
                comment = Comment.objects.get(comment_id=request.data['comment_id'])
                comment.dislike = Comment.objects.get(comment_id=request.data['comment_id']).dislike + 1
                comment.save()
                data = comment.dislike
            except:
                message = {"You have already disliked it"}
                return Response(data=message, status=status.HTTP_200_OK)
        else:
            message = {"Please enter according to the format"}
            return Response(data=message, status=status.HTTP_200_OK)

        return Response(data=data, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def cancel_comment_like(self, request):
        like_dislike = request.data['like_dislike']
        if like_dislike == 1:
            comment_id = request.data['comment_id']
            try:
                like = request.user.commentlike_set.get(comment_id=comment_id, uid=request.user.id)
                like.delete()
            except:
                message = {"Like cannot be less than 0"}
                return Response(data=message, status=status.HTTP_200_OK)

            comment = Comment.objects.get(comment_id=request.data['comment_id'])
            comment.like = Comment.objects.get(comment_id=request.data['comment_id']).like - 1
            comment.save()
            message = comment.like
        elif like_dislike == 0:
            comment_id = request.data['comment_id']
            try:
                dislike = request.user.commentlike_set.get(comment_id=comment_id, uid=request.user.id)
                dislike.delete()
            except:
                message = {"Dislike cannot be less than 0"}
                return Response(data=message, status=status.HTTP_200_OK)

            comment = Comment.objects.get(comment_id=request.data['comment_id'])
            comment.dislike = Comment.objects.get(comment_id=request.data['comment_id']).dislike - 1
            comment.save()
            message = comment.dislike
        else:
            message = {"Please enter according to the format"}
            return Response(data=message, status=status.HTTP_200_OK)

        return Response(data=message, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def update_faq_view(self, request):
        faq_id = request.data['faq_id']
        faq = FAQ.objects.get(id=faq_id)
        faq.view = faq.view + 1
        faq.save()
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def faq_list(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = request.data['page_size']
        query_set = FAQ.objects.all().order_by('order')
        result_page = paginator.paginate_queryset(query_set, request)
        serializer = FAQListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def my_post(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = request.data['page_size']
        query_set = NoticeBoard.objects.filter(uid=request.user.id).order_by('-post_id')
        result_page = paginator.paginate_queryset(query_set, request)
        serializer = PostListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK)