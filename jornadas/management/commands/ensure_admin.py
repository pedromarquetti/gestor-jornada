import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from jornadas.models import Role


class Command(BaseCommand):
    help = (
        "Cria ou atualiza o usuário administrador usando ADMIN_USER/ADMIN_PWD do .env."
    )

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USER", "admin")
        password = os.environ.get("ADMIN_PWD")
        if not password:
            self.stderr.write(
                self.style.ERROR("ADMIN_PWD não definido no ambiente ou no .env.")
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "role": Role.objects.get(name=Role.ADMIN),
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.role = Role.objects.get(name=Role.ADMIN)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "criado" if created else "atualizado"
        self.stdout.write(self.style.SUCCESS(f"Administrador '{username}' {action}."))
