from django.conf import settings
from django.db import models

from lexeme.models import Lexeme

from MyProject.models import SoftDeletionModel


class Post(SoftDeletionModel):
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    edited = models.BooleanField(default=False)
    date_created = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    lexeme = models.ForeignKey(Lexeme, related_name='posts', on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.id:
            self.edited = True
        super(Post, self).save(*args, **kwargs)

class Report(models.Model):
    message = models.CharField(max_length=100)
    post = models.ForeignKey(Post, related_name='reports', on_delete=models.CASCADE)
    date_created = models.DateTimeField(
         verbose_name='date joined', auto_now_add=True)
    report_from = models.ForeignKey('account.Account',on_delete=models.CASCADE, related_name='post_report_from')
    active = models.BooleanField(default=True)


