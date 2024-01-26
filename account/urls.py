from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

app_name = "account"
urlpatterns = [
    path('register/', registration_view, name='register'),
    path('test/', test, name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('me/', get_user_from_token, name='me'),
    path('update/', update_account, name='update'),
    path('newpassword/', update_password, name='update'),
    path('resetpassword/', reset_password, name='update'),
    path('users/<username>/', get_usernames_startwith, name='getusers'),
]