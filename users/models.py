from io import BytesIO

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from users.constants import (
    ABOUT_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
)


AVATAR_SIZE = 200
AVATAR_BACKGROUND_COLOR = (99, 102, 241)
AVATAR_TEXT_COLOR = (255, 255, 255)
AVATAR_FONT_SIZE = 96
AVATAR_FORMAT = 'PNG'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField(
        'Название',
        max_length=SKILL_NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None

    email = models.EmailField('Email', unique=True)
    name = models.CharField('Имя', max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField('Фамилия', max_length=USER_NAME_MAX_LENGTH)

    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True,
    )

    about = models.TextField(
        'О себе',
        max_length=ABOUT_MAX_LENGTH,
        blank=True,
    )

    phone = models.CharField(
        'Телефон',
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        null=True,
    )

    github_url = models.URLField('GitHub', blank=True)

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='users',
    )

    created_at = models.DateTimeField(
        'Дата регистрации',
        auto_now_add=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(
                self._generate_avatar_name(),
                self._generate_avatar_file(),
                save=False,
            )
        super().save(*args, **kwargs)

    def _generate_avatar_name(self):
        email_part = self.email.split('@')[0] if self.email else 'user'
        return f'{email_part}.png'

    def _generate_avatar_file(self):
        image = Image.new(
            'RGB',
            (AVATAR_SIZE, AVATAR_SIZE),
            AVATAR_BACKGROUND_COLOR,
        )
        draw = ImageDraw.Draw(image)

        letter = (self.name or self.email or 'U')[0].upper()

        try:
            font = ImageFont.truetype('arial.ttf', AVATAR_FONT_SIZE)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        position = (
            (AVATAR_SIZE - text_width) / 2,
            (AVATAR_SIZE - text_height) / 2,
        )

        draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format=AVATAR_FORMAT)
        return ContentFile(buffer.getvalue())

    def __str__(self):
        return f'{self.name} {self.surname}'.strip() or self.email
