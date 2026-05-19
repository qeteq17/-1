import re
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator


GITHUB_DOMAIN = 'github.com'
PHONE_RE = re.compile(r'^(?:8|\+7)\d{10}$')
URL_VALIDATOR = URLValidator(schemes=['http', 'https'])


def validate_github_url(github_url):
    github_url = github_url.strip()

    if not github_url:
        return github_url

    try:
        URL_VALIDATOR(github_url)
    except DjangoValidationError as error:
        raise forms.ValidationError('Укажите корректную ссылку.') from error

    hostname = (urlparse(github_url).hostname or '').lower()
    if hostname not in {GITHUB_DOMAIN, f'www.{GITHUB_DOMAIN}'}:
        raise forms.ValidationError(
            'Укажите корректную ссылку на GitHub-ресурс.'
        )

    return github_url


def normalize_phone(phone):
    phone = phone.strip()

    if not phone:
        raise forms.ValidationError(
            'Укажите номер телефона.'
        )

    if not PHONE_RE.match(phone):
        raise forms.ValidationError(
            'Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.'
        )

    if phone.startswith('8'):
        return f'+7{phone[1:]}'

    return phone


def validate_phone(phone):
    return normalize_phone(phone)
