from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from jornadas.models import Role, Task, User


class JornadasAdminTestCase(TestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="boss",
            email="boss@example.com",
            password="pw",
        )
        self.client.force_login(self.superuser)

    def test_models_are_registered(self):
        self.assertIn(Role, admin.site._registry)
        self.assertIn(User, admin.site._registry)
        self.assertIn(Task, admin.site._registry)

    def test_user_admin_includes_role(self):
        user_admin = admin.site._registry[User]

        fieldset_fields = [
            field for _, options in user_admin.fieldsets for field in options["fields"]
        ]
        add_fields = [
            field
            for _, options in user_admin.add_fieldsets
            for field in options["fields"]
        ]

        self.assertIn("role", fieldset_fields)
        self.assertIn("role", add_fields)

    def test_admin_index_and_changelists_render(self):
        urls = [
            reverse("admin:index"),
            reverse("admin:jornadas_role_changelist"),
            reverse("admin:jornadas_user_changelist"),
            reverse("admin:jornadas_task_changelist"),
            reverse("admin:jornadas_role_add"),
            reverse("admin:jornadas_user_add"),
            reverse("admin:jornadas_task_add"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_user_change_page_renders_with_role(self):
        user = get_user_model().objects.create_user(
            username="worker",
            password="pw",
            role=Role.objects.get(name=Role.USER),
        )

        response = self.client.get(
            reverse("admin:jornadas_user_change", args=[user.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="role"')

    def test_task_change_page_renders(self):
        task = Task.objects.create(
            user=self.superuser,
            activity="Revisão de relatório",
            started_at=timezone.now() - timedelta(hours=2),
            ended_at=timezone.now() - timedelta(hours=1),
        )

        response = self.client.get(
            reverse("admin:jornadas_task_change", args=[task.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revisão de relatório")
