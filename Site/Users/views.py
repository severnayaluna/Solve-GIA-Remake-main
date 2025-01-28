from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

# from aiogram import Bot

from MyUtils.views_wrappers import login_required, log_queries
# from KafkaUtils.Producer import producer
from SolveGia.models import *
from .forms import *

from random import randint
import json
from pprint import pprint


RUSSIAN_ALPHABET = list('абвгдеёжзийклмнопрстуфхцчшщьыъэюя'.upper())


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'Users/signup.html'


class MyLoginView(LoginView):
    success_url = reverse_lazy('profile')
    template_name = 'Users/login.html'


@login_required
@log_queries(False)
def profile(request):
    user = request.user
    print(user.get_groups())
    hws_pack = [{
        'group': group,
        'homeworks': [
            hw for hw in group.homeworks.select_related('variant', 'variant__category').all()
            ],
        } for group in
        CustomGroup.objects.prefetch_related(
            'homeworks'
            ).filter(id__in=user.get_groups())
    ]
    context = {
        'title': 'Profile',
        'russian_alphabet': RUSSIAN_ALPHABET,
        'classes': list(range(1, 12)),
        'cats': list(Category.objects.all().values_list('name', flat=True)),
        'user': user,
        'hws_pack': hws_pack,
        'groups': list(CustomGroup.objects.prefetch_related('users').filter(owner=user)),
    }

    if request.method == 'POST':
        action = request.POST.get('SUBMIT')
        if action == 'send':
            tg_id = int(request.POST.get('tg-id'))

            # if tg_id:

            #     code = ''.join([str(randint(1, 9)) for _ in range(5)])
            #     text = f'Your verefication code is `{code}`'
            #     msg = {
            #         'type': 'foo',
            #         'foo': {
            #             'name': 'send_message',
            #             'args': (),
            #             'kwargs': {
            #                 'chat_id': tg_id,
            #                 'text': text,
            #                 'parse_mode': 'MarkdownV2',
            #             },
            #         }
            #     }
            #     producer.produce('bot', json.dumps(msg).encode('ascii'))
            #     producer.flush()
            #     user.code = code
            #     user.save()
                # return redirect('profile')
            return redirect('profile')

        elif action == 'set':
            secret_code = request.POST.get('code')
            tg_id = int(request.POST.get('tg-id'))
            if user.code == secret_code:
                user.tg_id =tg_id
                user.code = None
                user.save()
            return redirect('profile')

        elif action == 'create-group':
            group_number = request.POST.get('class[]')
            group_let = request.POST.get('letter[]')
            group_cat = request.POST.get('cat[]')

            group_name = f'{group_number}-{group_let}-{group_cat}'

            new_group = CustomGroup(name=group_name, owner=user)
            new_group.save()

            return redirect('profile')

        elif action == 'set-hw':
            group = get_object_or_404(CustomGroup, pk=int(request.POST.get('set-hw-for-group[]')))
            variant = get_object_or_404(Variant, pk=int(request.POST.get('hw-variant-id')))

            new_hw = Homework(variant=variant)
            new_hw.save()

            group.homeworks.add(new_hw)

            return redirect('profile')

        elif action == 'add-user':
            group = get_object_or_404(CustomGroup, pk=int(request.POST.get('group[]')))
            sub_user = get_object_or_404(CustomUser, pk=int(request.POST.get('user-pk')))
            if sub_user.in_groups:
                sub_user.in_groups += f'.{group.pk}'
            else:
                sub_user.in_groups = f'{group.pk}'
            sub_user.save()
            group.users.add(sub_user)

            return redirect('profile')

    return render(request, template_name='Users/profile.html', context=context)
