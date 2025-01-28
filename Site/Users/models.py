from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class Status(models.Model):
    name = models.CharField(max_length=50)
    weight = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'<Status-{self.name}-{self.pk}>'


class CustomUser(AbstractUser):
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, default=2)
    tg_id = models.PositiveIntegerField(blank=True, null=True)
    solved = models.PositiveIntegerField(blank=True, null=True)
    failed = models.PositiveIntegerField(blank=True, null=True)
    code = models.CharField(max_length=5, blank=True, null=True)
    in_groups = models.CharField(max_length=500, blank=True, null=True)

    def profile_url(self):
        return reverse(
            'profile'
        )

    def __str__(self):
        return f'<CustomUser-{self.pk}-{self.username}>'

    def get_groups(self):
        if self.in_groups:
            return list(set(list(map(int, self.in_groups.split('.')))))
        return []
