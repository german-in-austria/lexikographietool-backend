from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

urlpatterns = [

    
    path('home/', get_home),
    path('location/', create_address),
    # path('locations/', get_locations),
    path('cards/', card_list),
    path('own_cards/', card_own),
    path('lexeme/', create_lexeme),
    path('dialect/', create_dialect),
    path('etymology/', create_etymology),
    path('pronunciation/', create_pronunciation),
    path('example/', create_example),
    path('lexemes_simple/', LexemeSimpleListView.as_view(), name='lexemes_simple'),
    path('varieties/<search>/', get_variety_list, name='dialects'),
    path('categories/', CategoryListView.as_view(), name='categoriesc'),
    path('lexeme_by_word/<word>/', lexeme_first_by_word),
    path('category/<pk>/', create_category_with_lexeme),
    path('category_create/', create_category),
    path('lexeme/<lexemeId>/', get_lexeme),
    path('restore/<lexemeId>/', restore_word),
    path('lexemes/', LexemeView.as_view()),
    path('lexeme/like/<lexemeId>/', like_lexeme),
    path('lexemes/random/',get_random_lexemes),
    path('lexemes/popular/',get_most_popular),
    path('lexemes/discussed/',get_most_discussed),
    path('lexemes/similar/<lexemeId>/',get_similar_lexemes),
    path('report/lexeme/<lexemeId>/', report_lexeme),
    path('reports/lexeme/', ReportView.as_view()),
    path('report/lexeme/deactivate/<reportId>/', deactive_report),
    path('reports/amount/', get_amount_of_reports_total),
    path('lexemes_count/', get_lexemes_count),
    path('lexemes_my_count/', get_my_lexemes_count),
    path('highscore/', HighscoreView.as_view()),
    path('identical/', get_lexemes_with_same_dialectWord_and_word),

]