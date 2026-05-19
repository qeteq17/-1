from django.conf import settings
from django.db import models

from projects.constants import NAME_MAX_LENGTH, STATUS_MAX_LENGTH


class Project(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )

    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    description = models.TextField('Описание', blank=True)
    github_url = models.URLField('GitHub', blank=True)

    status = models.CharField(
        'Статус',
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
    )

    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name
