from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


class Command(BaseCommand):
    help = 'Создаёт тестовых пользователей, навыки и проекты.'

    def handle(self, *args, **options):
        python = Skill.objects.get_or_create(name='Python')[0]
        django = Skill.objects.get_or_create(name='Django')[0]
        js = Skill.objects.get_or_create(name='JavaScript')[0]
        html = Skill.objects.get_or_create(name='HTML')[0]
        css = Skill.objects.get_or_create(name='CSS')[0]
        postgres = Skill.objects.get_or_create(name='PostgreSQL')[0]

        alice = self.create_user(
            email='alice@example.com',
            password='password123',
            name='Alice',
            surname='Ivanova',
            phone='81111111111',
            github_url='https://github.com/alice',
            about='Backend-разработчик. Работаю с Django и PostgreSQL.',
            skills=[python, django, postgres],
        )
        boris = self.create_user(
            email='boris@example.com',
            password='password123',
            name='Boris',
            surname='Petrov',
            phone='82222222222',
            github_url='https://github.com/boris',
            about='Frontend-разработчик. Интересуюсь JavaScript и интерфейсами.',
            skills=[python, js],
        )
        clara = self.create_user(
            email='clara@example.com',
            password='password123',
            name='Clara',
            surname='Sidorova',
            phone='83333333333',
            github_url='https://github.com/clara',
            about='Верстальщик. Делаю адаптивные страницы на HTML и CSS.',
            skills=[html, css, js],
        )

        self.create_project(
            name='Backend проект',
            description='Серверная часть приложения Team Finder.',
            github_url='https://github.com/qeteq17/teamfinder',
            status=Project.STATUS_OPEN,
            owner=alice,
            participants=[alice, boris],
        )
        self.create_project(
            name='Frontend проект',
            description='Интерфейс приложения Team Finder.',
            github_url='https://github.com/qeteq17/teamfinder',
            status=Project.STATUS_OPEN,
            owner=boris,
            participants=[boris, clara],
        )
        self.create_project(
            name='Лендинг проекта',
            description='Адаптивная страница проекта.',
            github_url='https://github.com/qeteq17/teamfinder',
            status=Project.STATUS_CLOSED,
            owner=clara,
            participants=[clara, alice],
        )

        self.stdout.write(self.style.SUCCESS('Тестовые данные созданы.'))

    def create_user(
        self,
        email,
        password,
        name,
        surname,
        phone,
        github_url,
        about,
        skills,
    ):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'surname': surname,
                'phone': phone,
                'github_url': github_url,
                'about': about,
            },
        )

        user.name = name
        user.surname = surname
        user.phone = phone
        user.github_url = github_url
        user.about = about

        if created:
            user.set_password(password)

        user.avatar.delete(save=False)
        user.avatar = None
        user.save()

        user.skills.set(skills)
        return user

    def create_project(
        self,
        name,
        description,
        github_url,
        status,
        owner,
        participants,
    ):
        project, _ = Project.objects.get_or_create(
            name=name,
            owner=owner,
            defaults={
                'description': description,
                'github_url': github_url,
                'status': status,
            },
        )

        project.description = description
        project.github_url = github_url
        project.status = status
        project.save()
        project.participants.set(participants)

        return project
