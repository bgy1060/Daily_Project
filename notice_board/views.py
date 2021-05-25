from django.contrib.auth import get_user_model
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from . import serializers
from .models import *
from .serializers import PostListSerializer, DetailPostSerializer, CommentListSerializer, CategoryListSerializer, \
    FAQListSerializer
from users.serializers import EmptySerializer
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from django.db.models import Q, Count

User = get_user_model()


class NoticeBoardViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = EmptySerializer
    serializer_classes = {

    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='글 제목'),
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='글 내용'),
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='카테고리 아이디'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def write_post(self, request):
        """ 새로운 글 쓰기 : title, content, category_id 입력 [token required] """
        data = request.data
        category_id = Category.objects.get(category_id=int(request.data['category_id']))
        request.user.noticeboard_set.create(title=data['title'], content=data['content'], date=timezone.now(),
                                            category_id=category_id, uid=request.user.id)

        point_action = Point_action.objects.get(action='게시물 작성')

        if Point_List.objects.filter(uid=request.user.id, date__year=timezone.now().year,
                                     date__month=timezone.now().month,
                                     date__day=timezone.now().day,
                                     action_id=point_action.id).count() >= point_action.limit_number_of_day:
            pass
        else:
            uid = CustomUser.objects.get(id=request.user.id)
            try:
                total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
                Point_List.objects.create(point=point_action.point_value,
                                          total_point=total_point + point_action.point_value,
                                          date=timezone.now(),
                                          action_id=point_action,
                                          detail_action='새로운 게시글 작성',
                                          uid=uid)
            except:
                Point_List.objects.create(point=point_action.point_value,
                                          total_point=point_action.point_value,
                                          date=timezone.now(),
                                          action_id=point_action,
                                          detail_action='새로운 게시글 작성',
                                          uid=uid)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='수정하고 싶은 글 post_id'),
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='수정 제목'),
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='수정 글 내용'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def update_post(self, request):
        """ 내가 작성한 글 수정 : title, content 수정 가능 [token required]"""
        data = request.data
        post_id = request.data['post_id']
        post = request.user.noticeboard_set.get(post_id=post_id)
        post.title = data['title']
        post.content = data['content']
        post.save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='삭제하고 싶은 글 post_id'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def delete_post(self, request):
        """ 내가 작성한 글 삭제 : post_id 필요 [token required]"""
        post_id = request.data['post_id']
        post = request.user.noticeboard_set.get(post_id=post_id)
        post.delete()

        point_action = Point_action.objects.get(action='게시글 삭제')
        uid = CustomUser.objects.get(id=request.user.id)
        try:
            total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=total_point + point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='작성한 게시글 삭제',
                                      uid=uid)
        except:
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='작성한 게시글 삭제',
                                      uid=uid)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='세부 내용을 보고싶은 글 post_id'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def detail_post(self, request):
        """ 특정 글의 세부 내용 : post_id 필요
            - "is_like_dislike": true 이면 좋아요/싫어요를 이미 누른 상태 (token 을 보내줘야만 확인 가능)
            - "editable": true 이면 수정 가능 (token을 보내줘야 확인 가능)
        """
        post_id = request.data['post_id']
        try:
            query_set = NoticeBoard.objects.get(post_id=post_id)
        except:
            return Response(data={"There is no post!"}, status=status.HTTP_200_OK)

        if request.user.is_anonymous:
            is_like_dislke = False
            editable = False
            like_dislike = -1
        else:
            try:
                n = NoticeBoardLike.objects.get(post_id=post_id, uid=request.user.id)
                is_like_dislke = True
                editable = request.user.id
                like_dislike = int(n.like_dislike)
            except:
                is_like_dislke = False
                editable = request.user.id
                like_dislike = -1

        serializer = DetailPostSerializer(query_set, context=[is_like_dislke, editable, like_dislike])
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='세부 내용을 보고싶은 댓글 comment_id'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def detail_comment(self, request):
        """ 변경된 댓글의 내용 확인 - comment_id를 보내면 해당 아이디의 댓글 내용을 보여줌
            - "is_like_dislike": true 이면 좋아요/싫어요를 이미 누른 상태 (token 을 보내줘야만 확인 가능)
            - "editable": true 이면 수정 가능 (token을 보내줘야 확인 가능)
        """
        comment_id = request.data['comment_id']

        query_set = Comment.objects.get(comment_id=comment_id)
        if request.user.is_anonymous:
            context = False
        else:
            context = request.user.id
        serializer = CommentListSerializer(query_set, context=context)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='post_id를 가진 글 조회수 업데이트'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def update_view(self, request):
        """ 특정 글의 조회수 업데이트 """
        post_id = request.data['post_id']
        post = NoticeBoard.objects.get(post_id=post_id)
        post.views = post.views + 1
        post.save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='post_id를 가진 글 조회수 조회'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def post_view(self, request):
        """ 특정 글의 조회수 가져오기 : post_id를 가진 글 조회수 가져오기"""
        post_id = request.data['post_id']
        post_view = NoticeBoard.objects.get(post_id=post_id).views
        return Response(data=post_view, status=status.HTTP_200_OK)

    @csrf_exempt
    @action(methods=['GET', ], detail=False)
    def category_list(self, request):
        """ 카테고리 목룍 가져오기 : 카테고리 리스트는 Admin 에서 관리"""
        query_set = Category.objects.all()
        serializer = CategoryListSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'page_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='한 페이지에 표시할 글 수'),
            'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='특정 카테고리를 가진 post를 보고싶을 경우'),
            'search_type': openapi.Schema(type=openapi.TYPE_STRING, description='검색 타입(제목만 검색, 내용만 검색, 제목+내용 검색)'),
            'search_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='검색 키워드'),
            'sort': openapi.Schema(type=openapi.TYPE_STRING, description='정렬 방법 디폴드 값은 최신순'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[])
    def post_list(self, request):
        """ 전체 글 목룍 가져오기 : category_id 필드가 all인 경우, 특정 카테고리의 전체 글 목록 가져오기 : category_id 필드에 특정 카테고리 작성
            검색어가 있다면 search_type에 검색 타입, search_keyword에 검색 키워드 작성. 검색어가 없다면 search_type, search_keyword를 null로 세팅하여 요청
            search_type에는 title_content, title, content가 존재
            sort에는 date(최신순), like(인기순), views(조회순), comment(댓글순)가 존재
        """

        paginator = PageNumberPagination()
        paginator.page_size = request.data['page_size']
        category_id = request.data['category_id']

        search_type = request.data['search_type']
        search_keyword = request.data['search_keyword']
        sort = request.data['sort']

        if category_id == 'all':
            if sort =='comment':
                query_set = NoticeBoard.objects.all().annotate(comment_count=Count('comment__post_id')).order_by('-comment_count')
            else:
                query_set = NoticeBoard.objects.all().order_by("-"+sort)
        else:
            if sort =='comment':
                query_set = NoticeBoard.objects.filter(category_id=category_id).annotate(comment_count=Count('comment__post_id')).order_by('-comment_count')
            else:
                query_set = NoticeBoard.objects.filter(category_id=category_id).order_by("-"+sort)

        if search_keyword and search_type:
            if search_type == 'title_content':
                query_set = query_set.filter(
                    Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword))

            elif search_type == 'title':
                query_set = query_set.filter(title__icontains=search_keyword)

            elif search_type == 'content':
                query_set = query_set.filter(content__icontains=search_keyword)

        result_page = paginator.paginate_queryset(query_set, request)
        serializer = PostListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='post_id를 가진 글의 댓글 가져오기'),
            'parent_comment': openapi.Schema(type=openapi.TYPE_INTEGER, description='특정 댓글의 대댓글을 조회할 때 사용'),

        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def comment_list(self, request):
        """ 전체 댓글 목록 가져오기 : parent_comment 필드 생략, 특정 댓글의 대댓글 조회 : parent_comment 에 대댓글을 보고 싶은 댓글의 comment_id 입력
            - "is_like_dislike": true 이면 좋아요/싫어요를 이미 누른 상태 (token 을 보내줘야만 확인 가능)
            - "editable": true 이면 수정 가능 (token을 보내줘야 확인 가능)
        """
        post_id = request.data['post_id']
        try:
            parent_comment = request.data['parent_comment']
            query_set = Comment.objects.filter(post_id=post_id).filter(parent_comment=parent_comment)
            if request.user.is_anonymous:
                context = False
            else:
                context = request.user.id
            serializer = CommentListSerializer(query_set, many=True, context=context)
        except:
            query_set = Comment.objects.filter(post_id=post_id).filter(parent_comment__isnull=True)
            if request.user.is_anonymous:
                context = False
            else:
                context = request.user.id
            serializer = CommentListSerializer(query_set, many=True, context=context)
        return JsonResponse(serializer.data, safe=False)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='post_id를 가진 글에 댓글 작성'),
            'comment_content': openapi.Schema(type=openapi.TYPE_STRING, description='댓글 내용'),
            'parent_comment': openapi.Schema(type=openapi.TYPE_INTEGER, description='대댓글을 작성할 경우 상위 댓글의 id 필요'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def write_comment(self, request):
        """ 댓글 작성하기 [token required]"""
        data = request.data
        post_id = NoticeBoard.objects.get(post_id=int(request.data['post_id']))
        point_action = Point_action.objects.get(action='댓글 작성')

        try:
            parent_comment = Comment.objects.get(comment_id=int(request.data['parent_comment']))
            request.user.comment_set.create(comment_content=data['comment_content'], date=timezone.now(),
                                            post_id=post_id, uid=request.user.id, parent_comment=parent_comment)

            if Point_List.objects.filter(uid=request.user.id, date__year=timezone.now().year,
                                         date__month=timezone.now().month,
                                         date__day=timezone.now().day).count() >= point_action.limit_number_of_day:
                pass
            else:
                uid = CustomUser.objects.get(id=request.user.id)
                try:
                    total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=total_point + point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='새로운 댓글 작성',
                                              uid=uid)
                except:
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='새로운 댓글 작성',
                                              uid=uid)
        except:
            request.user.comment_set.create(comment_content=data['comment_content'], date=timezone.now(),
                                            post_id=post_id, uid=request.user.id)
            if Point_List.objects.filter(uid=request.user.id, date__year=timezone.now().year,
                                         date__month=timezone.now().month,
                                         date__day=timezone.now().day,
                                         action_id=point_action.id).count() >= point_action.limit_number_of_day:
                pass
            else:
                uid = CustomUser.objects.get(id=request.user.id)
                try:
                    total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=total_point + point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='새로운 댓글 작성',
                                              uid=uid)
                except:
                    Point_List.objects.create(point=point_action.point_value,
                                              total_point=point_action.point_value,
                                              date=timezone.now(),
                                              action_id=point_action,
                                              detail_action='새로운 댓글 작성',
                                              uid=uid)

        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='수정하고 싶은 댓글 ID'),
            'comment_content': openapi.Schema(type=openapi.TYPE_STRING, description='수정할 댓글 내용'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def update_comment(self, request):
        """ 댓글 수정하기 [token required] """
        data = request.data
        comment_id = request.data['comment_id']
        comment = request.user.comment_set.get(comment_id=comment_id)
        comment.comment_content = data['comment_content']
        comment.save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='삭제할 댓글 ID'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def delete_comment(self, request):
        """ 댓글 삭제하기 [token required]"""
        comment_id = request.data['comment_id']
        comment = request.user.comment_set.get(comment_id=comment_id)
        comment.delete()

        point_action = Point_action.objects.get(action='댓글 삭제')
        uid = CustomUser.objects.get(id=request.user.id)
        try:
            total_point = Point_List.objects.filter(uid=request.user.id).order_by('-id')[0].total_point
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=total_point + point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='작성한 댓글 삭제',
                                      uid=uid)
        except:
            Point_List.objects.create(point=point_action.point_value,
                                      total_point=point_action.point_value,
                                      date=timezone.now(),
                                      action_id=point_action,
                                      detail_action='작성한 댓글 삭제',
                                      uid=uid)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요/싫어요 누를 글 ID'),
            'like_dislike': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요를 누르면 1, 싫어요를 누르면 0으로 setting'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_post_like(self, request):
        """ 게시글 좋아요 & 싫어요 누르기 : 좋아요를 누를 경우 like_dislike = 1로, 싫어요를 누를 경우 like_dislike = 0으로 설정 [token required]
            - 이미 게시글에 좋아요 & 싫어요를 눌렀을 경우 "You have already liked/disliked it 메세지 전송"
        """
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
                data = post.dislike
            except:
                message = {"You have already disliked it"}
                return Response(data=message, status=status.HTTP_200_OK)
        else:
            message = {"Please enter according to the format"}
            return Response(data=message, status=status.HTTP_200_OK)

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요/싫어요 취소할 글 ID'),
            'like_dislike': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요 취소는 1, 싫어요 취소는 0으로 setting'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def cancel_post_like(self, request):
        """ 게시글 좋아요 & 싫어요 취소하기 : 좋아요 취소는 like_dislike = 1으로, 싫어요 취소는 like_dislike = 0으로 설정 [token required]"""
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

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요/싫어요 누를 댓글 ID'),
            'like_dislike': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요를 누르면 1, 싫어요를 누르면 0으로 setting'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def add_comment_like(self, request):
        """ 댓글 좋아요 & 싫어요 누르기 : 좋아요를 누를 경우 like_dislike = 1로, 싫어요를 누를 경우 like_dislike = 0으로 설정 [token required]
            - 이미 댓글에 좋아요 & 싫어요를 눌렀을 경우 "You have already liked/disliked it 메세지 전송"
        """
        try:
            comment_id = Comment.objects.get(comment_id=int(request.data['comment_id']))
        except:
            message = {"The post has already been deleted and does not exist."}
            return Response(data=message, status=status.HTTP_200_OK)
        like_dislike = request.data['like_dislike']
        if like_dislike == 1:
            try:
                request.user.commentlike_set.create(like_dislike=like_dislike, comment_id=comment_id,
                                                    uid=request.user.id)
                comment = Comment.objects.get(comment_id=request.data['comment_id'])
                comment.like = Comment.objects.get(comment_id=request.data['comment_id']).like + 1
                comment.save()
                data = comment.like
            except:
                message = {"You have already liked it"}
                return Response(data=message, status=status.HTTP_200_OK)

        elif like_dislike == 0:
            try:
                request.user.commentlike_set.create(like_dislike=like_dislike, comment_id=comment_id,
                                                    uid=request.user.id)
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

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요/싫어요 취소할 댓글 ID'),
            'like_dislike': openapi.Schema(type=openapi.TYPE_INTEGER, description='좋아요 취소는 1, 싫어요 취소는 0으로 setting'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def cancel_comment_like(self, request):
        """ 댓글 좋아요 & 싫어요 취소하기 : : 좋아요 취소는 like_dislike = 1으로, 싫어요 취소는 like_dislike = 0으로 설정 [token required]"""
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

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'faq_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='조회수 업데이트할 FAQ ID'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def update_faq_view(self, request):
        """ FAQ 조회수 업데이트 """

        faq_id = request.data['faq_id']
        faq = FAQ.objects.get(id=faq_id)
        faq.view = faq.view + 1
        faq.save()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'page_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='한 페이지에 보여줄 FAQ 수'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False)
    def faq_list(self, request):
        """ FAQ 리스트 출력 """
        paginator = PageNumberPagination()
        paginator.page_size = request.data['page_size']
        query_set = FAQ.objects.all().order_by('order')
        result_page = paginator.paginate_queryset(query_set, request)
        serializer = FAQListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'page_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='한 페이지에 보여줄 내가 작성한 글 수'),
        }))
    @csrf_exempt
    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def my_post(self, request):
        """  내가 작성한 글 보기 [token required] """
        paginator = PageNumberPagination()
        paginator.page_size = request.data['page_size']
        query_set = NoticeBoard.objects.filter(uid=request.user.id).order_by('-post_id')
        result_page = paginator.paginate_queryset(query_set, request)
        serializer = PostListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_200_OK)
