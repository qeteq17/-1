from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q

from users.models import User
from users.validators import normalize_phone, validate_github_url


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError('Неверный имейл или пароль')

        return cleaned

    def get_user(self):
        return self.user_cache


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(label='Телефон', required=True)

    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url', '')
        return validate_github_url(github_url)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        normalized_phone = normalize_phone(phone)
        alternate_phone = f'8{normalized_phone[2:]}'

        duplicate_phone_exists = (
            User.objects.filter(
                Q(phone=normalized_phone) | Q(phone=alternate_phone)
            )
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if duplicate_phone_exists:
            raise forms.ValidationError(
                'Пользователь с таким номером телефона уже существует.'
            )

        return normalized_phone


class UserPasswordChangeForm(PasswordChangeForm):
    pass
