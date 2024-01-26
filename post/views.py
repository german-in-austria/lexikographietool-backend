from django.db.models import Q
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from .serializers import PostSerializer, PostSimpleSerializer, PostCreateSerializer, ReportCreateSerializer, \
    ReportSerializer
from .models import Post, Report
from rest_framework.response import Response

from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework import filters
from lexeme.pagination import MyPagination

from lexeme.permissions import IsSuperUser

from lexeme.views import MyCustomOrdering

from notification.models import Notification

from lexeme.models import Lexeme


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_post(request):
    account = request.user
    post = Post(author=account)
    if request.method == 'POST':
        serializer = PostCreateSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            #create notification
            notification = Notification()
            if 'lexeme' in request.data and request.data['lexeme'] is not None:
                print(type(request.data['lexeme']))
                try:

                    lexeme = Lexeme.objects.get(id=request.data['lexeme'])
                except Post.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                if lexeme.author.username != account.username:

                    notification.user = lexeme.author
                    notification.refers_to_lexeme = lexeme
                    notification.message = account.username + " hat deinen Beitrag kommentiert."
                    notification.save()
            if 'parent' in request.data and request.data['parent'] is not None:
                try:
                    parent = Post.objects.get(id=request.data['parent'])
                except Post.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                if parent.author.username != account.username:

                    notification.user = parent.author
                    notification.refers_to_posting = parent
                    notification.message = account.username + " hat deinen Beitrag kommentiert."
                    notification.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated, ])
def get_update_delete_post_by_id(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializers = PostSerializer(post)
        return Response(serializers.data)

    user = request.user
    if (post.author != user and not user.is_superuser):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_200_OK)

    if request.method == 'PUT':
        serializer = PostCreateSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_post_by_lexemes(request, lexemeId):
    if request.method == 'GET':
        posts = Post.objects.filter(lexeme=lexemeId)
        serializers = PostSimpleSerializer(posts, many=True)
        return Response(serializers.data)


@api_view(['GET'])
def get_answers_of_post(request, postId):
    if request.method == 'GET':
        posts = Post.objects.filter(parent=postId)
        serializers = PostSerializer(posts, many=True)
        return Response(serializers.data)

class PostView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = MyPagination
    pagination_class.page_size = 25
    filter_backends = [MyCustomOrdering,filters.SearchFilter]
    search_fields = ['text']

    def get_queryset(self):
        queryset = Post.objects.all()

        return queryset.filter(Q(parent__isnull=True) & Q(lexeme__isnull=True))

    def get_serializer_context(self):
        context = super(PostView, self).get_serializer_context()
        context.update({"request": self.request}, )
        return context

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_own_posts(request):
    account = request.user
    if request.method == 'GET':
        posts = Post.objects.filter(Q(parent=None) & Q(lexeme=None) & Q(author=account))
        serializers = PostSimpleSerializer(posts, many=True)
        return Response(serializers.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def report_post(request,postId):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=postId)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['post'] = post.id
        data['report_from'] = request.user.id

        serializer = ReportCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    serializer_class = ReportSerializer
    pagination_class = MyPagination
    pagination_class.page_size = 16
    filter_backends = [filters.OrderingFilter]
    queryset = Report.objects.all()

@api_view(['PUT'])
@permission_classes([IsAuthenticated, ])
def deactive_report(request,reportId):
    if request.method == 'PUT':
        try:
            report = Report.objects.get(id=reportId)
        except Report.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        report.active = not report.active
        report.save()
        return Response()