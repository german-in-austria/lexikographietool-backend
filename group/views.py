from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .serializers import GroupSerializer, GroupSettingsSerializer
from .serializers import GroupNameSerializer
from .models import Group, GroupSettings
from account.models import Account
import hashlib
import jwt
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.generics import ListAPIView
from lexeme.pagination import MyPagination
from rest_framework import filters
import datetime


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def create_group(request):
    account = request.user
    group = Group(owner=account)
    if request.method == 'POST':
        serializer = GroupSerializer(group, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def add_or_remove_user(request, groupId, username):
    try:
        group = Group.objects.get(pk=groupId)
        member = Account.objects.get(username=username)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if group.owner != user and not user.is_superuser:
        return Response({'response': 'You dont have permissions to add users to this group'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        group.members.add(member)
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    if request.method == 'DELETE':
        group.members.remove(member)
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_own_groups(request):
    account = request.user

    groups = Group.objects.filter(
        Q(owner=account) | Q(members=account)
    ).distinct()
    serializers = GroupNameSerializer(groups, many=True)
    return Response(serializers.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_own_groups_deleted(request):
    account = request.user

    groups = Group.all_objects.filter(
        Q(owner=account)
    ).distinct().dead()
    serializers = GroupSerializer(groups, many=True)
    return Response(serializers.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def restore_group(request, groupId):
    account = request.user
    try:
        group = Group.all_objects .get(id=groupId)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if group.owner != account:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    group.deleted_at = None
    group.save()
    serializer = GroupSerializer(group)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def get_update_group(request, groupId):
    account = request.user
    try:
        group = Group.objects.get(id=groupId)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    has_access = account.is_superuser or group.owner == account or account in group.members.all() or group.settings.public
    if not has_access:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        serializer = GroupSerializer(group, context={'account': account})
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        if group.owner != account and not account.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if group.owner != account and not account.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        group.delete()
        return Response()


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def leave_group(request, groupId):
    account = request.user
    try:
        group = Group.objects.get(id=groupId)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    group.members.remove(account)
    return Response()


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_invite_link(request, groupId):
    account = request.user
    try:
        group = Group.objects.get(id=groupId)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if group.owner != account:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    key = "secret"
    encoded = jwt.encode({"exp": datetime.datetime.utcnow(
    ) + datetime.timedelta(days=2000), "groupId": groupId}, key, algorithm="HS256")
    return Response(encoded)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def join_group(request, groupId):
    account = request.user
    try:
        group = Group.objects.get(id=groupId)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    #if public join is deactivated, hash is required
    if not group.settings.public_can_join:
        try:
            decoded = jwt.decode(request.data['hash'], "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if 'groupId' not in decoded or 'groupId' not in decoded and groupId != decoded['groupId']:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    if group.settings.need_password and group.settings.join_password != request.data['password']:
        return Response("Wrong password",status=status.HTTP_401_UNAUTHORIZED,)


    group.members.add(account)
    return Response()


class GroupView(ListAPIView):
    serializer_class = GroupSerializer
    pagination_class = MyPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = Group.objects.all()

        if self.request.user:
            user = self.request.user
            if 'all' in self.request.GET and user.is_superuser:
                print('hallo')
                return queryset.all()
            if 'public' in self.request.GET:
                public = self.request.GET['public']
                if public == 'False':
                    return queryset.filter(Q(owner=user) | Q(members=user)).distinct().order_by("date_created")
            else:
                return queryset.filter(Q(owner=user) | Q(members=user) | Q(settings__public=True)).distinct().order_by("date_created")
        return queryset.filter(settings__public=True).order_by("date_created")


@api_view(['GET'])
def get_group_name_by_id(request, groupId):
    try:
        group = Group.objects.get(id=groupId)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(GroupNameSerializer(group).data)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated, ])
def get_update_group_settings(request, groupId):
    account = request.user

    try:
        group = Group.objects.get(id=groupId)
    except GroupSettings.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    print(account.is_superuser)
    if group.owner != account and not account.is_superuser:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    settings = group.settings
    if request.method == 'GET':
        return Response(GroupSettingsSerializer(settings).data)

    if request.method == 'PUT':
        serializer = GroupSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
