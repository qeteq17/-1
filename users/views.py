import json
from json import JSONDecodeError
from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from users.constants import SKILLS_SEARCH_LIMIT, USERS_PER_PAGE
from users.forms import (
    LoginForm,
    ProfileForm,
    RegisterForm,
    UserPasswordChangeForm,
)
from users.models import Skill, User
from users.services import paginate_queryset


def register_view(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(reverse('projects:list'))

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    form = LoginForm(request, request.POST or None)

    if form.is_valid():
        login(request, form.get_user())
        return redirect(reverse('projects:list'))

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect(reverse('projects:list'))


def user_detail(request, user_id):
    user_obj = get_object_or_404(
        User.objects.prefetch_related(
            'skills',
            'owned_projects__participants',
        ),
        pk=user_id,
    )

    return render(
        request,
        'users/user-details.html',
        {
            'user': user_obj,
            'all_skills': Skill.objects.all(),
        },
    )


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if form.is_valid():
        form.save()
        messages.success(request, 'Профиль сохранён.')
        return redirect(reverse('users:detail', args=[request.user.id]))

    return render(
        request,
        'users/edit_profile.html',
        {'form': form, 'user': request.user},
    )


@login_required
def change_password(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Пароль успешно изменён.')
        return redirect(reverse('users:detail', args=[request.user.id]))

    return render(
        request,
        'users/change_password.html',
        {'form': form},
    )


def user_list(request):
    skill_name = request.GET.get('skill', '').strip()

    participants = User.objects.prefetch_related('skills').all().order_by('id')

    if skill_name:
        participants = participants.filter(skills__name__iexact=skill_name)

    page_obj = paginate_queryset(
        request,
        participants.distinct(),
        USERS_PER_PAGE,
    )

    all_skills = Skill.objects.all()

    return render(
        request,
        'users/participants.html',
        {
            'participants': page_obj.object_list,
            'page_obj': page_obj,
            'all_skills': all_skills,
            'skills': all_skills,
            'active_skill': skill_name,
        },
    )


def skill_search(request):
    search_query = request.GET.get('q', '').strip()

    skills_queryset = Skill.objects.all()

    if search_query:
        skills_queryset = skills_queryset.filter(name__istartswith=search_query)

    return JsonResponse(
        list(
            skills_queryset.order_by('name').values(
                'id',
                'name',
            )[:SKILLS_SEARCH_LIMIT]
        ),
        safe=False,
    )


@login_required
def add_skill(request, user_id):
    if request.user.id != user_id or request.method != 'POST':
        return HttpResponseForbidden()

    payload = _get_request_payload(request)
    skill_id = payload.get('skill_id')
    skill_name = (payload.get('name') or '').strip()

    skill = None
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif skill_name:
        skill, created = get_or_create_skill(skill_name)

    if not skill:
        return JsonResponse(
            {'error': 'invalid'},
            status=HTTPStatus.BAD_REQUEST,
        )

    already_added = request.user.skills.filter(pk=skill.pk).exists()

    if not already_added:
        request.user.skills.add(skill)

    return JsonResponse(
        {
            'skill_id': skill.id,
            'id': skill.id,
            'name': skill.name,
            'created': created,
            'added': not already_added,
        }
    )


@login_required
def remove_skill(request, user_id, skill_id):
    if request.user.id != user_id or request.method != 'POST':
        return HttpResponseForbidden()

    user_obj = get_object_or_404(User, pk=user_id)
    skill = get_object_or_404(Skill, pk=skill_id)

    if not user_obj.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {'error': 'skill_not_found'},
            status=HTTPStatus.BAD_REQUEST,
        )

    user_obj.skills.remove(skill)
    return JsonResponse({'status': 'ok'})


def _get_request_payload(request):
    if request.POST:
        return request.POST

    try:
        return json.loads(request.body.decode() or '{}')
    except (UnicodeDecodeError, JSONDecodeError):
        return {}


def get_or_create_skill(name):
    existing_skill = Skill.objects.filter(name__iexact=name).first()

    if existing_skill:
        return existing_skill, False

    return Skill.objects.create(name=name), True
