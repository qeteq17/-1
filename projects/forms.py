from django import forms

from projects.models import Project
from users.validators import validate_github_url

PROJECT_STATUS_FORM_CHOICES = [
    (Project.STATUS_OPEN, 'Открыт'),
    (Project.STATUS_CLOSED, 'Закрыт'),
]


class ProjectForm(forms.ModelForm):
    status = forms.ChoiceField(
        label='Статус',
        choices=PROJECT_STATUS_FORM_CHOICES,
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url', '')
        return validate_github_url(github_url)
