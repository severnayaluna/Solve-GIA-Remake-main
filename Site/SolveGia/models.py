from django.db import models
from django.shortcuts import reverse

from Users.models import CustomUser


User = CustomUser


class Task(models.Model):
    text = models.TextField()
    answer = models.TextField(blank=True, null=True)
    photos = models.TextField(blank=True)
    files = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(blank=True, default=0)

    class Meta:
        ordering = ['pk', 'rating']

    def __str__(self):
        return f'<Task-{self.pk}>'
    
    def get_absolute_url(self):
        return reverse(
            'show-task',
            kwargs={
                'task_id': self.pk,
            }
        )


class TypeNumber(models.Model):
    number = models.PositiveSmallIntegerField()
    tasks = models.ManyToManyField(Task, related_name='typentotasks')
    spec_time = models.PositiveIntegerField(default=0) # seconds


class Category(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=250)
    type_numbers = models.ManyToManyField(TypeNumber)
    amount_of_type_numbers = models.PositiveSmallIntegerField()

    def get_str_tns_for_infa(self):
        tns = [str(i) for i in range(1, 19)]
        tns.append('19-21')
        tns += [str(i) for i in range(22, 28)]
        return tns

    def __str__(self):
        return f'<Category-{self.name}>'
    
    def get_absolute_url(self):
        return reverse(
            'show-vars',
            kwargs={
                'cat_name': self.name,
                'page': 0,
            }
        )


class Variant(models.Model):
    tasks = models.ManyToManyField(Task, related_name='totasks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    median_rating = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'<Variant-{self.category.name}-{self.pk}>'
    
    def get_absolute_url(self):
        return reverse(
            'show-variant',
            kwargs={
                'cat_name': self.category.name,
                'var_id': self.pk,
                'answers': 'on',
            })


class Attempt(models.Model):
    solve_percent = models.FloatField()

    def __str__(self):
        return f'<Attempt-{self.solve_percent}>'


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempts = models.ManyToManyField(Attempt, related_name='toattempts')

    def __str__(self):
        return f'<Result-{self.user.username}-attempts:{len(self.attempts.all())}>'


class Homework(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    results = models.ManyToManyField(Result, related_name='toresults', null=True, blank=True)

    def __str__(self):
        return f'<Homework-{self.variant}-rs:{len(self.results.all())}>'


class CustomGroup(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(User, related_name='tocustomusers')
    homeworks = models.ManyToManyField(Homework, related_name='tohomeworks')

    def __str__(self):
        return f'<CustomGroup-{self.name}-hws:{len(self.homeworks.all())}>'

    def results_url(self):
        return reverse(
            'results',
            kwargs={
                'group_pk': self.pk
            }
        )
