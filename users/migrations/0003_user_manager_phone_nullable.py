# Generated for TeamFinder variant 2 completion.

from django.db import migrations, models

import users.models


def empty_phone_to_null(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.filter(phone='').update(phone=None)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(
                max_length=12,
                null=True,
                unique=True,
                verbose_name='Телефон',
            ),
        ),
        migrations.RunPython(empty_phone_to_null, migrations.RunPython.noop),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.UserManager()),
            ],
        ),
    ]
