from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models


class Role(models.Model):
    USER = "user"
    ADMIN = "admin"

    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Nome",
    )

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, *, role, **extra_fields):
        extra_fields["role"] = role
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        if "role" not in extra_fields:
            extra_fields["role"] = Role.objects.get(name=Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        verbose_name="Role",
        help_text=(
            "Permissões do usuário no sistema: 'admin' gerencia os dados de "
            "produtividade, 'user' registra apenas as próprias jornadas."
        ),
    )

    REQUIRED_FIELDS = ["email"]

    objects = UserManager()


class Task(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Usuário",
    )
    activity = models.CharField(
        max_length=200,
        verbose_name="Atividade realizada",
    )
    started_at = models.DateTimeField(verbose_name="Início")
    ended_at = models.DateTimeField(verbose_name="Término")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ended_at__gt=models.F("started_at")),
                name="jornadas_task_end_after_start",
            )
        ]
        indexes = [
            models.Index(fields=["user", "-started_at"]),
        ]

    def __str__(self):
        return self.activity
