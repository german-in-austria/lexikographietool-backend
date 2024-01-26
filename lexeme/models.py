from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from MyProject.models import SoftDeletionModel
import uuid

CHOICE_KIND = (
    ('N', 'noun'),
    ('V', 'verb'),
    ('Aj', 'adjective'),
    ('Av', 'adverb'),
    ('I', 'interjection'),
    ('P', 'phrase')
)

CHOICE_GENUS = (
    ('F', 'feminin'),
    ('M', 'verb'),
    ('N', 'neuter'),
)


class Address(models.Model):
    
    name = models.CharField(max_length=100, null=True, blank=True)
    osm_id = models.CharField(max_length=100, null=True, blank=True)
    osm_value = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    country_code = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.CharField(max_length=100, null=True,blank=True)
    place = models.CharField(max_length=100, null=True,blank=True)
    state = models.CharField(max_length=100, null=True,blank=True)
    state_code = models.CharField(max_length=100, null=True,blank=True)
    province = models.CharField(max_length=100, null=True,blank=True)
    province_code = models.CharField(max_length=100, null=True,blank=True)
    community = models.CharField(max_length=100, null=True,blank=True)
    community_code = models.CharField(max_length=100, null=True,blank=True)
    latitude = models.CharField(max_length=100, null=True,blank=True)
    longitude = models.CharField(max_length=100, null=True,blank=True)


class Lexeme(SoftDeletionModel):
    liked_from = models.ManyToManyField('account.Account', related_name='collections',through = 'LikeLexeme')
    date_created = models.DateTimeField(
         verbose_name='date joined', auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='lexemes')
    content = models.OneToOneField('LexemeContent',related_name='activeLexeme',on_delete=models.CASCADE,null=True)
    def save(self, *args, **kwargs):
        super(Lexeme, self).save(*args, **kwargs)


class LexemeContent(SoftDeletionModel):
    date_created = models.DateTimeField(
         verbose_name='date joined', auto_now_add=True)
    word = models.CharField(max_length=100, null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    variety = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField( null=True,blank=True)
    kind = models.CharField(max_length=255, choices=CHOICE_KIND,null=True)
    genus = models.CharField(max_length=255, choices=CHOICE_GENUS,null=True)
    dialectWord = models.CharField(max_length=100)
    origin = models.ForeignKey(Address, related_name='dialectWords', on_delete=models.CASCADE,null=True)
    sensitive = models.BooleanField(default=False)
    lexeme = models.ForeignKey(Lexeme, related_name='versions',on_delete=models.CASCADE,null=True)

class LikeLexeme(SoftDeletionModel):
    user = models.ForeignKey('account.Account',on_delete=models.CASCADE)
    lexeme = models.ForeignKey(Lexeme,on_delete=models.CASCADE,related_name="likes")
    like = models.BooleanField(default=False)
    date_updated = models.DateTimeField(auto_now=True)

    

    class Meta:
        unique_together = (("user", "lexeme"),)


class Category(models.Model):
    category = models.CharField(max_length=100, primary_key=True)
    lexemes = models.ManyToManyField(LexemeContent, related_name='categories')


class Example(models.Model):
    example = models.TextField()
    dialectWord = models.ForeignKey(LexemeContent, related_name='examples', on_delete=models.CASCADE)

    def __str__(self):
        return self.example


class Pronunciation(models.Model):
    pronunciation = models.CharField(max_length=100)
    dialectWord = models.ForeignKey(LexemeContent, related_name='pronunciations', on_delete=models.CASCADE)

    def __str__(self):
        return self.pronunciation


class Etymology(models.Model):
    etymology = models.TextField()
    dialectWord = models.ForeignKey(LexemeContent, related_name='etymologies', on_delete=models.CASCADE)

    def __str__(self):
        return self.etymology

class Report(models.Model):
    message = models.TextField()
    lexeme = models.ForeignKey(Lexeme, related_name='reports', on_delete=models.CASCADE)
    content = models.ForeignKey(LexemeContent, related_name='reports', on_delete=models.CASCADE)
    date_created = models.DateTimeField(
         verbose_name='date joined', auto_now_add=True)
    report_from = models.ForeignKey('account.Account',on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


