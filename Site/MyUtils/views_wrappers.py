from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import Http404, redirect
from django.db import connection, reset_queries

from time import time


def log_execution_time(foo: callable):
    def wrapper(*args, **kwargs):
        st = time()
        resp = foo(*args, **kwargs)
        et = time() - st

        print(f'---# Foo "pr" finished in {et}s #---')

        return resp
    return wrapper


def login_required(foo: callable):
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
            return redirect('login')

        resp = foo(*args, **kwargs)
        return resp

    return wrapper


def log_session(foo: callable):
    def wrapper(*args, **kwargs):
        request = args[0]
        results = list([f'{key}: {request.session[key]}'] for key in request.session.keys())
        print(results)
        resp = foo(*args, **kwargs)
        return resp

    return wrapper


def log_queries(print_queries: bool = True):
    def decorator(foo: callable):
        def wrapper(*args, **kwargs):
            reset_queries()
    
            st = time()

            resp = foo(*args, **kwargs)

            print(f'\n-----# Function "{foo.__name__}" was done in {round(time()-st, 5)}s #-----')
            print(f'-----# Queries count while calling "{foo.__name__}" was {len(connection.queries)} #-----\n')

            if print_queries:
                [print(f'  {ind + 1}:{query}\n') for ind, query in enumerate(connection.queries)]
            reset_queries()
            return resp

        return wrapper
    
    return decorator
