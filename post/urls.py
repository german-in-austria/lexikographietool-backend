from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


urlpatterns = [

    path('post/', create_post),
    path('post/<int:id>/', get_update_delete_post_by_id),
    path('posts/lexeme/<lexemeId>/', get_post_by_lexemes),
    path('posts/', PostView.as_view()),
    path('posts/<postId>/', get_answers_of_post),
    path('ownposts/', get_own_posts),
    path('report/post/<postId>/', report_post),
    path('reports/post/', ReportView.as_view()),
    path('report/post/deactivate/<reportId>/', deactive_report),

]