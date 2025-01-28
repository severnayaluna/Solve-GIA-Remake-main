import django
import os
import asyncio
import random
import time
from multiprocessing import Process, Value, Queue
from threading import Thread

from asgiref.sync import sync_to_async
from django.db import connection, reset_queries

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Site.settings')
django.setup()


from Users.models import *
from SolveGia.models import *
from SolveGia.views import get_task_closets_to_difficulty


User = CustomUser

# infa = Category.objects.get(pk=2)


admin_status = Status(name='teacher')
admin_status.save()
