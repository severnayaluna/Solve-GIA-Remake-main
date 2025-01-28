from django.shortcuts import render, redirect, get_object_or_404, Http404, reverse
from django.http import HttpRequest, HttpResponse
from django.db import connection, reset_queries
from django.db.models import Aggregate, Prefetch, Min, F, Avg, Q, Func, Value, Subquery, IntegerField
from django.db.models.functions import Abs

from multiprocessing import Process
import random
from math import ceil
import os
from pathlib import Path

from .models import Task, Category, Variant, Attempt, TypeNumber, Result, Homework, CustomGroup

from MyUtils.views_wrappers import *
import time
from pprint import pprint


BASE_DIR = Path(__file__).resolve().parent.parent


# @log_queries(False)
def get_task_closets_to_difficulty(type_number, difficulty):
    tasks = type_number.tasks\
    .filter(rating__lte=difficulty)\
    .annotate(delta=Func(F('rating') - difficulty, function='ABS'))\
    .order_by('delta')

    return random.choice(tasks.filter(delta=tasks.first().delta))

    for i, task in enumerate(tasks):
        if task.rating != tasks[0].rating:
            return random.choice(tasks[:i])


@log_queries(False)
def index(request: HttpRequest):
    categories = list(Category.objects.all())
    context = {
        'title': 'Main page',
        'categories': categories,
    }

    if request.method == 'POST':
        action = request.POST.get('SUBMIT')
        match action:
            case 'gen':
                category = get_object_or_404(Category, name=request.POST.get('category[]'))
                difficulty = request.POST.get('difficulty[]')
                answers = request.POST.get('answers')

                if not answers:
                    answers = 'off'

                if difficulty == '':
                    difficulty = random.randint(1, 100)

                return redirect(
                    'gen-r-var',
                    cat_name=category.name,
                    difficulty=difficulty,
                    answers=answers)

            case 'show-vars':
                category = get_object_or_404(Category, name=request.POST.get('category[]'))

                return redirect(
                    'show-vars',
                    cat_name=category.name,
                    page=0)

            case 'show-tasks':
                type_number = request.POST.get('type-number')
                cat_name = request.POST.get('category[]')
                return redirect(
                    'show-tasks',
                    cat_name=cat_name,
                    type_number=type_number
                    )

            case 'create':
                cat_name = request.POST.get('category[]')
                return redirect('create-variant', cat_name=cat_name)


    return render(request, template_name='SolveGia/index.html', context=context)


@log_queries(True)
def generate_random_variant(request: HttpRequest, cat_name, difficulty, answers):
    reset_queries()
    st = time.time()
    try:
        difficulty = int(difficulty)
    except TypeError:
        raise Http404

    if not (0 <= difficulty <= 100):
        raise Http404

    category = Category.objects\
    .prefetch_related('type_numbers')\
    .prefetch_related('type_numbers__tasks')\
    .get(name=cat_name)

    if answers == 'off':
        answers = False
    elif answers == 'on':
        answers = True
    else:
        raise Http404

    context = {
        'title': 'Random variant',
        'tasks': [],
        'answers': answers,
        'category': category,
    }
    tns = category.get_str_tns_for_infa()
    tasks = []

    type_numbers = category.type_numbers.all()

    for index, query in enumerate(type_numbers):
        tasks.append(get_task_closets_to_difficulty(query, difficulty))



    rating_sum = sum([t.rating for t in tasks])

    for i in range(1, category.amount_of_type_numbers):
        context['tasks'].append((tasks[i-1], tns[i-1]))


    new_var = Variant(category=category, median_rating=rating_sum // category.amount_of_type_numbers)
    new_var.save()
    new_var.tasks.set(tasks)

    # save_variant_process = Process(target=save_variant, args=(category,))
    # save_variant_process.start()

    context['time'] = time.time() - st
    if answers:
        return render(request, template_name='SolveGia/show-variant.html', context=context)
    else:
        redir = redirect('solve-variant', cat_name=cat_name, var_id=new_var.pk, task_number=1)
        return redir


@log_queries(True)
def show_vars(request, cat_name, page=0):
    category = get_object_or_404(Category, name=cat_name)

    if page < 0:
        raise Http404

    variants = Variant.objects.filter(category=category)[page * 20:(page * 20) + 20]

    context = {
        'title': f'All variants of {category.name} - p{page}',
        'variants': variants,
        'category': category,
    }

    return render(request, template_name='SolveGia/show-vars.html', context=context)


@log_queries(False)
def show_variant(request, cat_name, var_id, answers):
    st = time.time()
    category = get_object_or_404(Category, name=cat_name)

    if answers == 'off':
        answers = False
    elif answers == 'on':
        answers = True
    else:
        raise Http404

    variant = get_object_or_404(Variant, pk=var_id, category=category)
    tasks = list(variant.tasks.all())
    tns = category.get_str_tns_for_infa()
    context = {
        'title': f'Variant №{variant.pk}({variant.median_rating})',
        'tasks': [(tasks[i-1], tns[i-1]) for i in range(1, category.amount_of_type_numbers + 1)],
        'variant': variant,
        'answers': answers,
    }
    context['time'] = time.time() - st
    return render(request, template_name='SolveGia/show-variant.html', context=context)


@log_queries(False)
def show_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    context = {
        'title': f'Task №{task.pk}',
        'task': task,
    }

    return render(request, template_name='SolveGia/show-task.html', context=context)


@log_queries(False)
def solve_variant(request: HttpRequest, cat_name, var_id, task_number=1):
    category = get_object_or_404(Category, name=cat_name)
    variant = get_object_or_404(Variant, pk=var_id)
    if task_number > category.amount_of_type_numbers:
        raise Http404

    context = {
        'title': f'Variant №{variant.pk}({variant.median_rating})',
        'task': (variant.tasks.all()[task_number - 1], category.get_str_tns_for_infa()[task_number - 1]),
    }

    try:
        current_number_of_session = request.session[f'var-{var_id}']
        if int(current_number_of_session) != task_number:
            redir = redirect('solve-variant', cat_name=cat_name, var_id=var_id, task_number=current_number_of_session)
            redir.set_cookie('time', '0')
            return redir
        else:
            rend = render(request, template_name='SolveGia/solve-variant.html', context=context)
    except KeyError:
        context['task'] = (variant.tasks.all()[0], category.get_str_tns_for_infa()[0]),
        redir = redirect('solve-variant', cat_name=cat_name, var_id=var_id, task_number=1)
        request.session[f'var-{variant.pk}'] = 1
        redir.set_cookie('time', '0')
        return redir

    if request.method == 'POST':
        answer = request.POST.get('answer')
        time = int(request.COOKIES['time'])


        request.session[f'v-{var_id}-a-{task_number}'] = {
            'answer': answer,
            'time': time,
        }
        results = list([f'{key}: {request.session[key]}'] for key in request.session.keys())
        print(results)

        """
        Мега умная формула которая считает сложность В ПРОЦЕНТАХ...
        Потом сохраняем сложность в бд.
        """

        if task_number < category.amount_of_type_numbers:
            current_number_of_session = request.session[f'var-{var_id}']
            redir = redirect('solve-variant', cat_name=cat_name, var_id=var_id, task_number=task_number + 1)
            redir.set_cookie('time', '0')
            request.session[f'var-{var_id}'] = str(int(current_number_of_session) + 1)
            return redir
        else:
            redir = redirect('home')
            results = list([f'{key}: {request.session[key]}'] for key in request.session.keys())
            for i in range(1, category.amount_of_type_numbers + 1):
                del request.session[f'v-{var_id}-a-{i}']
            del request.session[f'var-{var_id}']
            redir.delete_cookie('time')
            return redir

    return rend


@log_queries(False)
def show_tasks_of_type(request, cat_name, type_number):
    category = get_object_or_404(Category, name=cat_name)
    type_number = get_object_or_404(category.type_numbers.all(), number=type_number)

    context = {
        'title': f'All tasks №{type_number.number} of {category.name}',
        'tasks': list(type_number.tasks.all()),
        'number': category.get_str_tns_for_infa()[type_number.number-1],
    }

    return render(request, template_name='SolveGia/show-tasks.html', context=context)


@log_queries(False)
def create_variant(request, cat_name):
    category = get_object_or_404(Category, name=cat_name)

    if request.method == 'POST':
        tasks_pks = [
            list(map(int, list(request.POST.getlist(f'tasks-{tn}-[]'))))
            if request.POST.getlist(f'tasks-{tn}-[]') is not None else []
            for tn in category.get_str_tns_for_infa()
            ]
        pprint(tasks_pks)


    cache_page_path = BASE_DIR / 'templates' / 'Cache' / f'{category.name}-create-variant-cache.html'
    if os.path.exists(cache_page_path):
        return render(request, template_name=f'Cache/{category.name}-create-variant-cache.html')

    context = {
        'title': 'Variant creater',
        'task_pack': [(
            number, [task for task in list(tn.tasks.order_by('rating').values_list('pk', 'rating'))]
            ) for number, tn in zip(category.get_str_tns_for_infa(), category.type_numbers.all())
            ],
    }

    return render(request, template_name='SolveGia/create-variant.html', context=context)


def solve_homework(request, group_pk, hw_pk):
    return render(request, template_name='SolveGia/in-dev.html')


def results(request, group_pk):
    group = get_object_or_404(CustomGroup, pk=group_pk)

    context = {
        'title': f'Results of {group.name}',
    }

    hws_results_pack = [
        {
            'variant': hw.variant,
            'results': [
                {
                    'user': res.user,
                    'tries': res.attempts.count(),
                    'percent': res.attempts.all().order_by('-pk')[0].solve_percent,
                 }
                 for res in list(hw.results.all())
            ]
        }
        for hw in list(group.homeworks.all())
    ]
    context['results_table'] = hws_results_pack
    return render(request, template_name='SolveGia/results.html', context=context)
