from rest_framework import mixins
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from django.template.loader import render_to_string
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import RegistrationSerializer, UserSerializer, UserNameSerializer, UpdatePasswordSerializer
from .models import Account

import secrets
import string


@api_view(['GET', ])
def test(request):

    send_mail(
        'Subject here',
        'Here is the message.',
        'lexiktool@outlook.de',
        ['andreas@olschnoegger.at'],
        fail_silently=False,
    )
    return Response()


@api_view(['POST', ])
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)
    data = {}

    if serializer.is_valid():
        account = serializer.save()
        data['response'] = "successfully registered a new user."
        data['email'] = account.email.lower()
        data['username'] = account.username
        token = Token.objects.get(user=account).key
        data['token'] = token

        return Response(data)
    else:
        data = serializer.errors
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def get_user_from_token(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def get_usernames_startwith(request, username):
    user = Account.objects.filter(username__istartswith=username)
    serializer = UserNameSerializer(user, many=True)
    return Response(serializer.data)


@api_view(['PUT', ])
@permission_classes([IsAuthenticated, ])
def update_account(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', ])
@permission_classes([IsAuthenticated, ])
def update_password(request):
    user = request.user
    serializer = UpdatePasswordSerializer(
        user, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response()
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
def reset_password(request):
    if not 'email' in request.data:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    email = request.data['email']
    try:
        user = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    alphabet = string.ascii_letters + string.digits
    newPassword = ''.join(secrets.choice(alphabet)
                          for i in range(20))  # for a 20-character password

    user.set_password(newPassword)
    user.save()
    send_mail('Neues Password', u'Hallo {}, \ndein Passwort wurde erfolgreich zurückgesetzt lautet:\n{}\n\nDu kannst in den Profileinstellungen dein Passwort wieder ändern.\nWir wünschen dir noch viel Spaß auf Wortgut!'.format(user.username,newPassword), 'noreply@dioe.at',
              [email], fail_silently=False, )
    return Response()
