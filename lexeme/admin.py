from django.contrib import admin
from .models import *

admin.site.register(Lexeme)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(LexemeContent)