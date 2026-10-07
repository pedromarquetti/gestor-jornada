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
