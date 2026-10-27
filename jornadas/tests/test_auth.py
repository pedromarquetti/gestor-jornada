from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase

from ..models import Role

User = get_user_model()


class UserFixtures:
    """User fixtures for tests."""

    @staticmethod
    def create_user(username, email, password, role, **extra):
        """Create a user with the given role."""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **extra,
        )

    @classmethod
    def admin(cls, username="admin_user", email="admin@example.com", password="AdminPass123!", **extra):
        return cls.create_user(username, email, password, Role.objects.get(name=Role.ADMIN), **extra)

    @classmethod
    def user(cls, username="user_jornadas", email="user@example.com", password="UserPass123!", **extra):
        return cls.create_user(username, email, password, Role.objects.get(name=Role.USER), **extra)


class AuthFlowTests(TestCase):
    """Tests for the authentication flow."""

    def test_login_page_renders(self):
        """The login page renders at its named URL."""
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_rejects_invalid_credentials(self):
        """Invalid credentials do not create an authenticated session."""
        response = self.client.post(
            "/login/",
            {
                "username": "nonexistent_user",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_login_authenticates_valid_user(self):
        """Valid credentials redirect to home and create a session."""
        user = UserFixtures.admin(password="AdminPass123!")
        response = self.client.post(
            "/login/",
            {
                "username": user.username,
                "password": "AdminPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response["Location"])
        self.assertIn("_auth_user_id", self.client.session)
        user.delete()

    def test_session_persists_across_requests(self):
        """The authenticated session survives a second request."""
        user = UserFixtures.admin(password="AdminPass123!")
        self.client.post(
            "/login/",
            {
                "username": user.username,
                "password": "AdminPass123!",
            },
        )

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(user.username, response.content.decode())
        self.assertIn("admin", response.content.decode())
        user.delete()

    def test_role_persists_from_database(self):
        """Authorization reads the persisted role from the database."""
        user = UserFixtures.admin(password="AdminPass123!")
        self.client.post(
            "/login/",
            {
                "username": user.username,
                "password": "AdminPass123!",
            },
        )

        # Change the user's role in the database
        user.role = Role.objects.get(name=Role.USER)
        user.save()

        # The home page should show the updated role
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.content.decode())
        user.delete()

    def test_home_redirects_anonymous_to_login(self):
        """Anonymous users are redirected to the login page."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_home_requires_authentication(self):
        """Authenticated users can access the home page."""
        user = UserFixtures.admin(password="AdminPass123!")
        self.client.post(
            "/login/",
            {
                "username": user.username,
                "password": "AdminPass123!",
            },
        )

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        user.delete()

    def test_logout_removes_access_to_home(self):
        """Logout removes access to the protected home page."""
        user = UserFixtures.admin(password="AdminPass123!")
        self.client.post(
            "/login/",
            {
                "username": user.username,
                "password": "AdminPass123!",
            },
        )

        self.client.post("/logout/")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])
        user.delete()

    def test_next_redirect_only_allows_safe_destinations(self):
        """The next redirect only accepts safe destinations and does not create an open redirect."""
        user = UserFixtures.admin(password="AdminPass123!")
        # Safe next to home
        response = self.client.post(
            "/login/?next=/",
            {
                "username": user.username,
                "password": "AdminPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response["Location"])
        self.client.logout()

        # Unsafe external redirect should not be followed
        response = self.client.post(
            "/login/?next=https://evil.com/",
            {
                "username": user.username,
                "password": "AdminPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        # Should redirect to safe destination (home), not external
        self.assertNotIn("evil.com", response["Location"])
        user.delete()
