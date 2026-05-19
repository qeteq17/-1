from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import Skill, User


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'email',
        'name',
        'surname',
        'skills_list',
        'projects_count',
        'is_staff',
    )
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Личные данные',
            {'fields': ('name', 'surname', 'avatar', 'about', 'phone', 'github_url', 'skills')},
        ),
        (
            'Права',
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')},
        ),
        ('Важные даты', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'name', 'surname', 'password1', 'password2'),
            },
        ),
    )
    search_fields = ('email', 'name', 'surname')
    filter_horizontal = ('groups', 'user_permissions', 'skills')

    @admin.display(description='Навыки')
    def skills_list(self, obj):
        return ', '.join(obj.skills.values_list('name', flat=True))

    @admin.display(description='Участник проектов')
    def projects_count(self, obj):
        return obj.participated_projects.count()
