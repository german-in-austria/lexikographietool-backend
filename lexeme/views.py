from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters
from post.models import Post
from post.models import Report as PostReport
from MyProject import rulemanager
from .pagination import MyPagination
from .serializers import *
from .models import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
import random
from django.db.models import Count
from .permissions import IsSuperUser
from datetime import datetime, timedelta

from account.models import Account
from datetime import date, timedelta
from django.core import serializers


class MyCustomOrdering(filters.OrderingFilter):
    allowed_fields = ['content', 'word', 'dialectWord', 'kind',
                      'dialect', 'categories', 'description','author']
    allowed_custom_filters = ['content', 'dialectWord', '-dialectWord',
                              'date_created', '-date_created', 'word', '-word','author']

    # def get_ordering(self, request, queryset, view):

    # params = request.query_params.get(self.ordering_param)
    # if params:
    #     fields = [param.strip() for param in params.split(',')]
    #     # care with that - this will alow only custom ordering!
    #     ordering = [f for f in fields if f in self.allowed_custom_filters]

    #     if ordering:
    #         return ordering

    # No ordering was included, or all the ordering fields were invalid
    # return self.get_default_ordering(view)
    # ordering = super().get_ordering(request, queryset, view)
    # field_map = {
    #     'y': 'x__y',
    # }
    # return [field_map.get(o, o) for o in ordering]

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            queryset = queryset.order_by(*ordering)

        flt = {}

        for param in request.query_params:
            for fld in self.allowed_fields:

                if param.startswith(fld):
                    flt[param] = request.query_params[param]

        return queryset.filter(**flt)


# Lexeme


@api_view(['GET'])
def get_most_popular(request):
    if request.method == 'GET':
        countlist = LikeLexeme.objects.filter(Q(date_updated__gte=datetime.now(
        ) - timedelta(days=14)) & Q(like=True)).values('lexeme').annotate(total=Count('lexeme')).order_by('-total')
        id_list = countlist.values_list('lexeme', flat=True)
        id_list = id_list[0:5]
        lexemes = Lexeme.objects.filter(pk__in=id_list)
        return Response(CardSerializer(lexemes, many=True, context={'request': request}).data)


@api_view(['GET'])
def get_most_discussed(request):
    if request.method == 'GET':
        countlist = Post.objects.filter(Q(date_created__gte=datetime.now(
        ) - timedelta(days=14))).values(
            'lexeme').annotate(total=Count('lexeme')).order_by('-total')

        id_list = countlist.values_list('lexeme', flat=True)
        id_list = id_list[0:5]
        lexemes = Lexeme.objects.filter(pk__in=id_list)
        return Response(CardSerializer(lexemes, many=True, context={'request': request}).data)


@api_view(['GET'])
def card_list(request):
    if request.method == 'GET':
        cards = Lexeme.objects.all()
        serializers = CardSerializer(cards, many=True)
        return Response(serializers.data)


@api_view(['GET'])
def get_random_lexemes(request):
    if request.method == 'GET':
        lexeme_id_list = Lexeme.objects.all().values_list('id', flat=True)

        random_lexeme_list = random.sample(
            list(lexeme_id_list), min(len(lexeme_id_list), 5))

        cards = list(Lexeme.objects.filter(id__in=random_lexeme_list))
        random.shuffle(cards)
        serializers = CardSerializer(
            cards, many=True, context={'request': request})
        return Response(serializers.data)


@api_view(['GET'])
def card_list(request):
    if request.method == 'GET':
        cards = Lexeme.objects.all()
        serializers = CardSerializer(cards, many=True)
        return Response(serializers.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def card_own(request):
    account = request.user
    if request.method == 'GET':
        cards = Lexeme.objects.filter(author=account)
        serializers = CardSerializer(cards, many=True)
        return Response(serializers.data)


@api_view(['GET', 'PUT', 'DELETE'])
def get_lexeme(request, lexemeId):
    try:
        lexeme = Lexeme.objects.get(id=lexemeId)
    except Lexeme.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializers = CardSerializer(lexeme, context={'request': request})
        return Response(serializers.data)

    if request.method == 'PUT':
        account = request.user
        data = request.data
        data['lexeme'] = lexeme.id

        serializer = LexemeContentCreateSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            s = LexemeCreateSerializer(lexeme, data={'content': serializer.data['id']})
            if s.is_valid():
                s.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        account = request.user
        if request.user and request.user.is_superuser:
            lexeme.delete()
            return Response()
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def restore_word(request, lexemeId):
    try:
        lexeme = Lexeme.all_objects.get(id=lexemeId)
    except Lexeme.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.user and request.user.is_superuser:
        lexeme.deleted_at = None
        lexeme.save()
        return Response()
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def lexeme_first_by_word(request, word):
    lexemes = Lexeme.objects.filter(word=word)
    if len(lexemes) != 0:
        serializer = LexemeDetailSerializer(lexemes[0])
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


class LexemeSimpleListView(ListAPIView):
    queryset = Lexeme.objects.all()
    serializer_class = LexemeSimpleSerializer
    filter_backends = [SearchFilter]
    search_fields = ['content__word']


class LexemeView(ListAPIView):
    serializer_class = CardSerializer
    pagination_class = MyPagination
    pagination_class.page_size = 16
    filter_backends = [MyCustomOrdering, filters.SearchFilter]
    ordering_fields = ['content__word', 'content__dialectWord', 'date_created']
    search_fields = ['content__word', 'content__dialectWord', 'content__description', 'content__variety',
                     'content__categories__category', 'content__kind', 'author__username']

    def get_serializer_context(self):
        collection = -1
        if 'in_collection' in self.request.GET:
            collection = self.request.GET['in_collection']
        context = super(LexemeView, self).get_serializer_context()
        context.update({"request": self.request, "collectionId": collection}, )
        return context

    def get_queryset(self):
        queryset = Lexeme.objects.all()
        if self.request.auth is None or not self.request.user.show_sensitive_words:
            queryset = queryset.filter(content__sensitive=False)
        print('hoi')

        # get lexemes from collection
        if 'collection' in self.request.GET:
            collectionId = self.request.GET['collection']
            try:
                collection = Collection.objects.get(id=collectionId)
            except Lexeme.DoesNotExist:
                return Lexeme.objects.none()
            # check if collection is public or user is owner of collection
            if not rulemanager.can_see_lexemes_of_collection(collection, self.request.user):
                return Lexeme.objects.none()
            queryset = queryset.filter(Q(collections=collection) & Q(collectionlexeme__deleted_at__isnull=True))
        if 'mine' in self.request.GET and self.request.user:
            queryset = queryset.filter(author=self.request.user)

        return queryset.order_by("date_created")


@api_view(['GET'])
def get_lexemes_count(request):
    return Response(Lexeme.objects.all().count())


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_my_lexemes_count(request):
    return Response(Lexeme.objects.filter(author=request.user).count())

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def get_lexemes_with_same_dialectWord_and_word(request):
    account = request.user
    if request.method == 'POST':

        if 'word' not in request.data:
            return Response([])
        lexemes = Lexeme.objects.filter(Q(content__dialectWord__iexact=request.data['dialectWord']) & Q(content__word__iexact= request.data['word']))

        serializers = CardSerializer(lexemes,many=True)
        return Response(serializers.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_lexeme(request):
    account = request.user
    if request.method == 'POST':

        lexeme = Lexeme(author=account)
        lexeme.save()
        data = request.data
        data['lexeme'] = lexeme.id

        serializer = LexemeContentCreateSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            s = LexemeCreateSerializer(lexeme, data={'content': serializer.data['id']})
            if s.is_valid():
                try:
                    s.save()
                except:
                    lexeme.hard_delete()
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        lexeme.hard_delete()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def like_lexeme(request, lexemeId):
    account = request.user
    try:
        lexeme = Lexeme.objects.get(id=lexemeId)
    except Lexeme.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        like = LikeLexeme.objects.filter(Q(lexeme=lexeme) & Q(user=account))

        if len(like) == 0:
            like = LikeLexeme(user=account, lexeme=lexeme, like=True)
            like.save()
            print('leer')
        else:
            like = like[0]
            like.like = True
            like.save()
        return Response(status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        like = LikeLexeme.objects.filter(Q(lexeme=lexeme) & Q(user=account))

        if len(like) == 0:
            like = LikeLexeme(user=account, lexeme=lexeme, like=False)
            like.save()
            print('leer')
        else:
            like = like[0]
            like.like = False
            like.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_similar_lexemes(request, lexemeId):
    print(request.GET)
    try:
        lexeme = Lexeme.objects.get(pk=lexemeId)
    except Lexeme.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if 'dialectword' in request.GET:
        similars = Lexeme.objects.filter(Q(content__dialectWord__iexact=lexeme.content.dialectWord) &
                                         ~Q(content__word__iexact=lexeme.content.word)).exclude(
            id=lexemeId).distinct("content__word")
    elif 'word' in request.GET:
        similars = Lexeme.objects.filter(Q(content__word__gt='') &
                                         Q(content__word__isnull=False) &
                                         Q(content__word__iexact=lexeme.content.word) &
                                         ~Q(content__dialectWord__iexact=lexeme.content.dialectWord)).exclude(
            id=lexemeId)
    else:
        similars = Lexeme.objects.filter(Q(content__word__gt='') &
                                         Q(content__word__isnull=False) &
                                         Q(content__word__iexact=lexeme.content.word) &
                                         Q(content__dialectWord__iexact=lexeme.content.dialectWord)).exclude(
            id=lexemeId).distinct(
            "content__dialectWord")

    return Response(LexemeSimpleSerializer(similars, many=True).data)


# Dialect


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_dialect(request):
    if request.method == 'POST':
        try:
            dialect = Dialect.objects.get(dialect=request.data['dialect'])
        except Dialect.DoesNotExist:
            serializer = DialectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = DialectSerializer(dialect)
        return Response(serializer.data)


@api_view(['GET'])
def get_variety_list(request, search):
    if request.method == 'GET':
        varieties = LexemeContent.objects.filter(variety__icontains=search).distinct().values_list('variety', flat=True)
        return Response(varieties, status=status.HTTP_200_OK)


# Etymology


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_etymology(request):
    if request.method == 'POST':
        serializer = EtymologySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Pronunciation


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_pronunciation(request):
    if request.method == 'POST':
        serializer = PronunciationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Example
@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_example(request):
    if request.method == 'POST':
        serializer = ExampleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Category


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_category_with_lexeme(request, pk):
    lexeme = LexemeContent.objects.get(pk=pk)
    category, created = Category.objects.get_or_create(
        category=request.data['category'])
    serializer = CategorySerializer(category)
    category.lexemes.add(lexeme)
    if created:
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_category(request):
    category, created = Category.objects.get_or_create(
        category=request.data['category'])
    serializer = CategorySerializer(category)
    if created:
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListView(ListAPIView):
    pagination_class = MyPagination
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['category']


# Origin
@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_home(request):
    account = request.user
    location = account.home
    serializers = LocationSerializer(location)
    return Response(serializers.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_address(request):
    if request.method == 'POST':
        serializer = LocationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def get_locations(request):
#     if request.method == 'GET':
#         if 'zip' in request.GET:
#             locations = Address.objects.filter(
#                 zipcode__startswith=request.GET['zip'])
#         elif 'place' in request.GET:
#             locations = Address.objects.filter(
#                 place__icontains=request.GET['place'])
#         else:
#             return Response()
#     serializers = ZipPlaceSerializer(locations, many=True)
#     return Response(serializers.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def report_lexeme(request, lexemeId):
    if request.method == 'POST':
        try:
            lexeme = Lexeme.objects.get(id=lexemeId)
        except Lexeme.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['lexeme'] = lexeme.id
        data['content'] = lexeme.content.id
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
def deactive_report(request, reportId):
    if request.method == 'PUT':
        try:
            report = Report.objects.get(id=reportId)
        except Report.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        report.active = not report.active
        report.save()
        return Response()


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_amount_of_reports_total(request):
    if request.method == 'GET':
        number_of_reports = Report.objects.filter(active=True).count() + PostReport.objects.filter(active=True).count()
        return Response(number_of_reports)


class HighscoreView(ListAPIView):
    serializer_class = HighscoreSerializer
    pagination_class = MyPagination
    pagination_class.page_size = 4

    def get_queryset(self):
        highscore = Account.objects
        if 'daysPast' in self.request.GET:
            dateTil = date.today() - timedelta(days=int(self.request.GET['daysPast']))
            highscore = highscore.filter(lexemes__date_created__gte=dateTil)
        highscore = highscore.annotate(Count('lexemes')).order_by('-lexemes__count')
        return highscore
