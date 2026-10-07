from datetime import UTC, datetime, timedelta

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


class TaskQuerySetTestCase(TestCase):
    def setUp(self):
        role = Role.objects.get(name=Role.USER)
        User = get_user_model()
        self.user = User.objects.create_user(
            username="worker", password="pw", role=role
        )
        self.other = User.objects.create_user(
            username="other", password="pw", role=role
        )

    def make_task(self, started_at, ended_at, activity="Revisão de relatório"):
        return Task.objects.create(
            user=self.user,
            activity=activity,
            started_at=started_at,
            ended_at=ended_at,
        )

    def test_with_duration_annotates_timedelta(self):
        start = timezone.now() - timedelta(hours=2)
        task = self.make_task(start, start + timedelta(hours=1, minutes=30))

        annotated = Task.objects.with_duration().get(pk=task.pk)

        self.assertEqual(annotated.duration, timedelta(hours=1, minutes=30))

    def test_aware_datetimes_roundtrip_through_sqlite(self):
        start = datetime(2026, 1, 5, 8, 0, tzinfo=UTC)
        task = self.make_task(start, start + timedelta(hours=4))

        refetched = Task.objects.get(pk=task.pk)

        self.assertTrue(timezone.is_aware(refetched.started_at))
        self.assertEqual(refetched.started_at, start)
        self.assertEqual(refetched.ended_at, start + timedelta(hours=4))

    def test_for_user_filters(self):
        self.make_task(timezone.now(), timezone.now() + timedelta(hours=1))
        other_task = Task.objects.create(
            user=self.other,
            activity="Trabalho do outro",
            started_at=timezone.now() + timedelta(hours=2),
            ended_at=timezone.now() + timedelta(hours=3),
        )

        self.assertEqual(
            list(Task.objects.for_user(self.user).values_list("pk", flat=True)),
            [self.user.tasks.get().pk],
        )
        self.assertEqual(
            list(Task.objects.for_user(self.other).values_list("pk", flat=True)),
            [other_task.pk],
        )

    def test_between_filters_by_started_at(self):
        window_start = timezone.now() - timedelta(days=7)
        window_end = timezone.now()

        inside = self.make_task(
            window_start + timedelta(hours=1), window_start + timedelta(hours=2)
        )
        outside = self.make_task(
            window_end + timedelta(hours=1), window_end + timedelta(hours=2)
        )

        self.assertEqual(
            list(
                Task.objects.between(window_start, window_end).values_list(
                    "pk", flat=True
                )
            ),
            [inside.pk],
        )
        self.assertNotIn(
            outside.pk,
            Task.objects.between(window_start, window_end).values_list("pk", flat=True),
        )

    def test_total_hours_sums_durations_in_python(self):
        start = timezone.now() - timedelta(hours=6)
        self.make_task(start, start + timedelta(hours=1))
        self.make_task(
            start + timedelta(hours=2), start + timedelta(hours=3, minutes=30)
        )
        self.make_task(
            start + timedelta(hours=4), start + timedelta(hours=4, minutes=30)
        )

        self.assertEqual(Task.objects.total_hours(), 3.0)

    def test_total_hours_after_for_user_and_between(self):
        start = timezone.now() - timedelta(days=2)
        self.make_task(start, start + timedelta(hours=2))
        Task.objects.create(
            user=self.other,
            activity="Fora da janela",
            started_at=timezone.now(),
            ended_at=timezone.now() + timedelta(hours=9),
        )
        self.make_task(
            timezone.now() + timedelta(days=1),
            timezone.now() + timedelta(days=1, hours=1),
        )

        self.assertEqual(
            Task.objects.for_user(self.user)
            .between(start, timezone.now())
            .total_hours(),
            2.0,
        )
