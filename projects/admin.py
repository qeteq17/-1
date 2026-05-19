from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'status',
        'participants_count',
        'created_at',
    )
    list_editable = ('status',)
    search_fields = (
        'name',
        'description',
        'owner__email',
        'owner__name',
        'owner__surname',
    )
    list_filter = ('status',)
    filter_horizontal = ('participants',)

    @admin.display(description='Участники')
    def participants_count(self, obj):
        return obj.participants.count()
