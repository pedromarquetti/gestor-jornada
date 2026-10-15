import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from jornadas.models import Role


class EnsureAdminCommandTestCase(TestCase):
    def setUp(self):
        self.admin_role = Role.objects.get(name=Role.ADMIN)

    @patch.dict(os.environ, {"ADMIN_USER": "admin", "ADMIN_PWD": "super-secret"})
    def test_creates_superuser_with_admin_role(self):
        call_command("ensure_admin")

        User = get_user_model()
        user = User.objects.get(username="admin")
        self.assertEqual(user.role, self.admin_role)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("super-secret"))
        self.assertFalse(user.check_password("wrong"))

    @patch.dict(os.environ, {"ADMIN_USER": "admin", "ADMIN_PWD": "super-secret"})
    def test_is_idempotent(self):
        call_command("ensure_admin")
        call_command("ensure_admin")

        User = get_user_model()
        self.assertEqual(User.objects.filter(username="admin").count(), 1)

    @patch.dict(
        os.environ,
        {"ADMIN_USER": "admin", "ADMIN_PWD": "first-password"},
        clear=False,
    )
    def test_updates_password_when_env_changes(self):
        call_command("ensure_admin")

        with patch.dict(os.environ, {"ADMIN_PWD": "second-password"}, clear=False):
            call_command("ensure_admin")

        User = get_user_model()
        user = User.objects.get(username="admin")
        self.assertTrue(user.check_password("second-password"))
        self.assertFalse(user.check_password("first-password"))

    @patch.dict(os.environ, {"ADMIN_PWD": ""}, clear=True)
    def test_fails_without_admin_pwd(self):
        err = StringIO()
        call_command("ensure_admin", stdout=StringIO(), stderr=err)

        self.assertIn("ADMIN_PWD", err.getvalue())
        User = get_user_model()
        self.assertEqual(User.objects.count(), 0)
