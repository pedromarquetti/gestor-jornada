from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from jornadas.models import Role


class RoleTestCase(TestCase):
    def test_str_returns_name(self):
        self.assertEqual(str(Role.objects.get(name=Role.ADMIN)), "admin")

    def test_seed_migration_creates_both_roles(self):
        seeded = set(Role.objects.values_list("name", flat=True))
        self.assertEqual(seeded, {Role.USER, Role.ADMIN})

    def test_ordering_is_by_name(self):
        names = list(Role.objects.values_list("name", flat=True))
        self.assertEqual(names, sorted(names))

    def test_name_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Role.objects.create(name=Role.ADMIN)

    def test_verbose_names_are_set(self):
        meta = Role._meta
        self.assertEqual(str(meta.verbose_name), "Role")
        self.assertEqual(str(meta.verbose_name_plural), "Roles")


class UserTestCase(TestCase):
    def setUp(self):
        self.admin_role = Role.objects.get(name=Role.ADMIN)
        self.user_role = Role.objects.get(name=Role.USER)

    def test_auth_user_model_is_wired(self):
        self.assertEqual(get_user_model()._meta.label, "jornadas.User")

    def test_create_user_stores_password_hashed(self):
        user = get_user_model().objects.create_user(
            username="ana",
            email="Ana@Example.COM",
            password="s3nh4-forte",
            role=self.user_role,
        )
        self.assertNotIn("s3nh4-forte", user.password)
        self.assertTrue(user.password.startswith("pbkdf2_"))
        self.assertTrue(user.check_password("s3nh4-forte"))

    def test_create_user_normalizes_email(self):
        user = get_user_model().objects.create_user(
            username="ana",
            email="Ana@Example.COM",
            password="s3nh4-forte",
            role=self.user_role,
        )
        self.assertEqual(user.email, "Ana@example.com")

    def test_create_user_requires_a_role(self):
        with self.assertRaises(TypeError):
            get_user_model().objects.create_user(
                username="ana",
                password="s3nh4-forte",
            )

    def test_create_user_is_not_staff(self):
        user = get_user_model().objects.create_user(
            username="ana",
            password="s3nh4-forte",
            role=self.user_role,
        )
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_defaults_to_admin_role(self):
        user = get_user_model().objects.create_superuser(
            username="gestor",
            email="gestor@example.com",
            password="s3nh4-forte",
        )
        self.assertEqual(user.role, self.admin_role)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_honours_explicit_role(self):
        user = get_user_model().objects.create_superuser(
            username="gestor",
            email="gestor@example.com",
            password="s3nh4-forte",
            role=self.user_role,
        )
        self.assertEqual(user.role, self.user_role)
        self.assertTrue(user.is_staff)

    def test_user_can_authenticate(self):
        get_user_model().objects.create_user(
            username="ana",
            password="s3nh4-forte",
            role=self.user_role,
        )
        self.assertIsNotNone(authenticate(username="ana", password="s3nh4-forte"))
        self.assertIsNone(authenticate(username="ana", password="errada"))

    def test_role_is_required_at_the_database_level(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            get_user_model().objects.create(username="no-role")

    def test_role_in_use_cannot_be_deleted(self):
        get_user_model().objects.create_user(
            username="ana",
            password="s3nh4-forte",
            role=self.user_role,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.user_role.delete()

    def test_related_name_lists_users_of_a_role(self):
        get_user_model().objects.create_user(
            username="ana",
            password="s3nh4-forte",
            role=self.user_role,
        )
        self.assertEqual(
            [u.username for u in self.user_role.users.all()],
            ["ana"],
        )
