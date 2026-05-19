from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from projects.constants import PROJECTS_PER_PAGE
from projects.forms import ProjectForm
from projects.models import Project
from projects.services import get_projects_queryset
from users.services import paginate_queryset


def project_list(request):
    projects = get_projects_queryset()
    page_obj = paginate_queryset(request, projects, PROJECTS_PER_PAGE)

    return render(
        request,
        'projects/project_list.html',
        {'projects': page_obj.object_list, 'page_obj': page_obj},
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        get_projects_queryset(),
        pk=project_id,
    )

    return render(
        request,
        'projects/project-details.html',
        {'project': project},
    )


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(reverse('projects:detail', args=[project.id]))

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False},
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return HttpResponseForbidden('Редактировать можно только свой проект.')

    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        form.save()
        return redirect(reverse('projects:detail', args=[project.id]))

    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': True, 'project': project},
    )


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if (
        project.owner != request.user
        or request.method != 'POST'
        or project.status != Project.STATUS_OPEN
    ):
        return HttpResponseForbidden()

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=['status', 'updated_at'])

    return JsonResponse(
        {'status': 'ok', 'project_status': Project.STATUS_CLOSED}
    )


@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method != 'POST':
        return HttpResponseForbidden()

    if request.user == project.owner:
        return JsonResponse({'status': 'ok', 'participant': False})

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        return JsonResponse({'status': 'ok', 'participant': False})

    project.participants.add(request.user)
    return JsonResponse({'status': 'ok', 'participant': True})
