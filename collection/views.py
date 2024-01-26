from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .models import Collection, CollectionLexeme
from .serializers import CollectionSerializer, CollectionSimpleSerializer, CollectionUpdateSerializer
from lexeme.models import Lexeme
from lexeme.serializers import CardSerializer
from group.models import Group
from rest_framework.generics import ListAPIView
from lexeme.pagination import MyPagination
from rest_framework import filters

from group.serializers import GroupCollectionSerializer

from MyProject import rulemanager
@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def create_collection(request):
    account = request.user
    print(account)
    collection = Collection(author=account)
    if request.method == 'POST':
        serializer = CollectionSerializer(collection, data=request.data,context={request:request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_collections_by_owner(request):
    account = request.user
    collections = Collection.objects.filter(author=account)
    serializer = CollectionSerializer(collections, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_collections_deleted_by_owner(request):
    account = request.user
    collections = Collection.all_objects.filter(author=account).dead()
    serializer = CollectionSerializer(collections, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_collections(request):
    account = request.user
    collections = Collection.objects.filter(
        Q(author=account) | Q(group__members=account)
    ).distinct()
    serializer = CollectionSimpleSerializer(collections, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def restore_collection(request,collectionId):
    account = request.user
    try:
        collection = Collection.all_objects .get(id=collectionId)
    except Collection.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if collection.author != account:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    collection.deleted_at = None
    collection.save()
    serializer = CollectionSimpleSerializer(collection)
    return Response(serializer.data)


class CollectionView(ListAPIView):
    serializer_class = CollectionSimpleSerializer
    pagination_class = MyPagination
    pagination_class.page_size = 16

    filter_backends = [filters.SearchFilter]
    search_fields = ['name','description']

    def get_queryset(self):
        if self.request.user:
            user = self.request.user
            if 'public' in self.request.GET:
                public = self.request.GET['public']
                if public == 'False':
                    if 'group' in self.request.GET:
                        return Collection.objects.filter((Q(group__members=user) | Q(group__owner=user)) & Q(group=self.request.GET['group'])).distinct().order_by("date_created")
                    return Collection.objects.filter(Q(author=user) & Q(group__isnull=True)).distinct().order_by("date_created")
                return Collection.objects.filter(Q(public=True)).order_by("date_created")
            #Filtering by group
            if('group' in self.request.GET):
                try:
                    group = Group.objects.get(id=self.request.GET['group'])
                except Group.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            if user.is_superuser:
                return Collection.objects.filter( Q(group=group)).distinct().order_by("date_created")

            return Collection.objects.filter((Q(author=user) | Q(group__members=user) |  Q(group__owner=user) | Q(public=True))& Q(group=group)).distinct().order_by("date_created")
        return Collection.objects.filter(public=True).distinct().order_by("date_created")

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_lexemes_in_collection(request,collectionId):
    #Get ids of not deleted lexemes
    lexemeIds = CollectionLexeme.objects.filter(collection=collectionId).values_list('lexeme',flat=True)
    
    lexemes = Lexeme.objects.filter(id__in=lexemeIds)
    serializer = CardSerializer(lexemes, many=True,context={'request':request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_deleted_lexemes_in_collection(request,collectionId):
    #Get ids of not deleted lexemes
    lexemeIds = CollectionLexeme.all_objects.filter(collection=collectionId).dead().values_list('lexeme',flat=True)
    lexemes = Lexeme.objects.filter(id__in=lexemeIds)
    serializer = CardSerializer(lexemes, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT','DELETE'])
@permission_classes([IsAuthenticated, ])
def get_update_collection(request, collectionId):
    account = request.user
    try:
        collection = Collection.objects.get(id=collectionId)
    except Collection.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        has_access = account.is_superuser or collection.author == account or collection.public or\
                     collection.group != None and (account == collection.group.owner or \
                                                   account in collection.group.members.all())


        if not has_access:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = CollectionSerializer(collection,context={'request':request,'account':account})
        return Response(serializer.data)

    if request.method == 'PUT':
        if not collection.author == account :
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = CollectionUpdateSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not collection.author == account :
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        collection.delete()
        return Response(status=status.HTTP_200_OK)

@api_view(['PUT', 'DELETE', ])
@permission_classes([IsAuthenticated, ])
def add_or_remove_lexeme_to_collection(request, collectionId, lexemeId):
    account = request.user
    try:
        collection = Collection.objects.get(id=collectionId)
        lexeme = Lexeme.objects.get(id=lexemeId)
    except Lexeme.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Collection.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
        
    
    if request.method == 'PUT':
        #check permissions
        if not rulemanager.can_add_lexeme_to_collection(collection,account):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # check if already deleted
        collectionlexeme = CollectionLexeme.all_objects.filter(Q(lexeme=lexeme) & Q(collection=collection))
        if len(collectionlexeme) != 0:
            collectionlexeme = collectionlexeme[0]
            collectionlexeme.deleted_at = None
            collectionlexeme.save(request=request)
            serializer = CollectionSerializer(collectionlexeme.collection,context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        collectionLexeme = CollectionLexeme(collection=collection,lexeme=lexeme)
        collectionLexeme.save(request=request)
        return Response(status=status.HTTP_200_OK)


    if request.method == 'DELETE':
        if not rulemanager.can_remove_lexeme_from_collection(collection,account):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        collection.lexemes.remove(lexeme)
        return Response(status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, ])
def add_group_to_collection(request, collectionId, groupId):
    account = request.user
    try:
        collection = Collection.objects.get(id=collectionId)
        group = Group.objects.get(id=groupId)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Collection.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

    if not rulemanager.can_add_collection_to_group(group,account):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        collection.group = group
        collection.save()
        serializer = CollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_collections_split_by_group(request):
    account = request.user
    own_collections = Collection.objects.filter(
        Q(author=account) | Q(group__members=account)
    ).distinct()
    groups = groups = Group.objects.filter(
        Q(owner=account) | Q(members=account)
    ).distinct()
    groups = GroupCollectionSerializer(
        [{'id': -1, 'name': "Eigene Sammlung", 'collections': own_collections}] + list(groups), many=True)

    return Response(groups.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_collections_split_by_group_and_lexeme(request, lexemeId):
    account = request.user
    own_collections = Collection.objects.filter(
        Q(author=account) | Q(group__members=account)
    ).distinct()
    groups = groups = Group.objects.filter(
        Q(owner=account) | Q(members=account)
    ).distinct()
    groups = GroupCollectionSerializer(
        [{'id': -1, 'name': "Eigene Sammlung", 'collections': own_collections}] + list(groups), many=True,
        context={'lexeme_id': lexemeId})

    return Response(groups.data)


@api_view(['PUT', 'DELETE', ])
@permission_classes([IsAuthenticated, ])
def add_or_remove_lexeme_to_favorites(request, lexemeId):
    account = request.user
    try:
        collection = account.favorite
        lexeme = Lexeme.objects.get(id=lexemeId)
    except Lexeme.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return add_or_remove_lexeme_to_collection(request._request,collection.id,lexemeId)

