from MyProject.models import SoftDeletionModel
from django.db import models

from django.conf import settings
from lexeme.models import Lexeme
from post.models import Post


class Notification(SoftDeletionModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    refers_to_lexeme = models.ForeignKey(Lexeme, on_delete=models.CASCADE, null=True)
    refers_to_posting = models.ForeignKey(Post, on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)