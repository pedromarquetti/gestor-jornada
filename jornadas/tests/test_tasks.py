from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from jornadas.models import Role, Task


class TaskTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="worker",
            password="pw",
            role=Role.objects.get(name=Role.USER),
        )

    def make_task(self, started_at, ended_at, activity="Revisão de relatório"):
        return Task.objects.create(
            user=self.user,
            activity=activity,
            started_at=started_at,
            ended_at=ended_at,
        )

    def test_orders_by_started_at_desc(self):
        earlier = self.make_task(
            timezone.now() - timedelta(hours=5),
            timezone.now() - timedelta(hours=4),
        )
        later = self.make_task(
            timezone.now() - timedelta(hours=2),
            timezone.now() - timedelta(hours=1),
        )

        self.assertEqual(
            list(Task.objects.values_list("pk", flat=True)),
            [later.pk, earlier.pk],
        )

    def test_related_name_user_tasks(self):
        task = self.make_task(timezone.now(), timezone.now() + timedelta(hours=1))

        self.assertEqual(
            list(self.user.tasks.values_list("pk", flat=True)),
            [task.pk],
        )

    def test_cascade_delete_user(self):
        self.make_task(timezone.now(), timezone.now() + timedelta(hours=1))

        self.user.delete()

        self.assertEqual(Task.objects.count(), 0)

    def test_check_rejects_ended_before_started(self):
        with self.assertRaises(IntegrityError):
            self.make_task(
                timezone.now() + timedelta(hours=2),
                timezone.now() + timedelta(hours=1),
            )

    def test_check_rejects_equal_datetimes(self):
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            self.make_task(now, now)

    def test_str_is_activity(self):
        task = self.make_task(timezone.now(), timezone.now() + timedelta(hours=1))

        self.assertEqual(str(task), "Revisão de relatório")
