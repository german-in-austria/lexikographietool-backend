from django.conf import settings
from django.db import models

from lexeme.models import Lexeme, Category
from group.models import Group
from MyProject.models import SoftDeletionModel


class Collection(SoftDeletionModel):
    name = models.fields.CharField(max_length=100)
    description = models.fields.CharField(
        max_length=100, null=True, blank=True)
    lexemes = models.ManyToManyField(Lexeme, related_name='collections',through = 'CollectionLexeme')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              null=True, blank=True, related_name='collections')
    public = models.fields.BooleanField(default=False)
    organization = models.fields.CharField(
        max_length=100, null=True, blank=True)
    categories = models.ManyToManyField(Category,null=True,blank=True)

    can_add_lexemes_group = models.BooleanField(default=False)
    can_remove_lexemes_group = models.BooleanField(default=False)

    can_add_lexemes_public = models.BooleanField(default=False)
    can_remove_lexemes_public = models.BooleanField(default=False)
    date_created = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)

class CollectionLexeme(SoftDeletionModel):
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE)
    lexeme = models.ForeignKey(Lexeme,on_delete=models.CASCADE)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)

    def save(self,request, *args, **kwargs):
        if request:
            self.added_by = request.user
            
        super(CollectionLexeme,self).save(*args, **kwargs)

