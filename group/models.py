from django.conf import settings
from django.db import models

from MyProject.models import SoftDeletionModel

class GroupSettings(models.Model):
    members_create_collection = models.BooleanField(default=True)

    public_create_collection = models.BooleanField(default=False)
    public_can_join = models.BooleanField(default=False)

    need_password = models.BooleanField(default=False)
    join_password = models.CharField(max_length=100, null=True,blank=True)

    public = models.BooleanField(default=False)


class Group(SoftDeletionModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='groupsOwned', on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='groups')
    organization = models.CharField(max_length=100, null=True)
    settings = models.OneToOneField(
        GroupSettings, related_name='group', on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)

    def __str__(self):
        return self.name + str(self.id)

    def save(self, *args, **kwargs):
        if not self.pk:
            settings = GroupSettings()
            settings.save()
            self.settings = settings
        super(Group, self).save(*args, **kwargs)