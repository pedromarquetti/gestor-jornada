# gestorjornada

UNIVESP *Projeto Integrador* — a Django app to register and evaluate work-shift
activities ("jornadas"). Employees log what they did with a start/end time;
managers review productivity as charts. Django 5.2 (LTS) on Python 3.14,
SQLite. `README.md` is the roadmap and is written in pt-BR — read it before
scoping work.

Current state: the DB plan is complete. `jornadas`
ships `Role` (seeded `user`/`admin` by `0002_seed_roles`), `User` (custom
`AUTH_USER_MODEL` with a `role` FK), and `Task` with an end-after-start CHECK
and a `(user_id, started_at DESC)` index; `TaskQuerySet` adds `with_duration`,
`for_user`, `between`, and `total_hours`. All three models are registered in
the admin, and `ensure_admin` recreates the superuser from `.env`. Next up from
the roadmap: the task-tracking UI, API, charts, and Docker — nothing is wired
beyond `/admin/`. 

## Read the Django docs first

This project targets Django 5.2. **Fetch the current 5.2 docs before writing
any Django code** — do not work from memory or from pre-4.0 tutorials.

- Cheat sheet / upgrade notes: <https://docs.djangoproject.com/en/5.2/topics/cheatsheet/>
- Release notes (check what changed in 5.2 vs 4.x): <https://docs.djangoproject.com/en/5.2/releases/5.2/>
- Models & queries: <https://docs.djangoproject.com/en/5.2/topics/db/>
- Class-based views: <https://docs.djangoproject.com/en/5.2/topics/class-based-views/>
- Templates, forms, security, deployment, testing: same base URL.

If the installed Django version differs from the version you're reading docs
for, stop and say so — do not mix APIs. Verify with
`python3 -m django --version`.

## Repository layout

The git repo root and the Django project root are **different directories**.
This trips up nearly every command:

```
gestor/                  <- Django project root: where manage.py lives, NOT in git
├── manage.py            run every management command from here
├── AGENTS.md        this file
├── README.md        pt-BR roadmap (the source of truth for scope)
├── .gitignore
├── db.sqlite3           0 bytes, gitignored
└── gestorjornada/       <- git repo root; the Python package
    ├── settings.py      single-file settings, .env loaded via python-dotenv
    ├── urls.py          only /admin/ is wired
    └── wsgi.py, asgi.py
```

The `jornadas` app holds the domain models and is the only app. Create
further apps as `python manage.py startapp <app>` and register them in
`INSTALLED_APPS`.

## Commands

```bash
python manage.py migrate
python manage.py makemigrations <app>
python manage.py runserver
python manage.py test
python manage.py check
python manage.py ensure_admin   # create/update admin from ADMIN_USER/ADMIN_PWD
ruff check .                     # lint
ruff format .                    # auto-format, Black-compatible
```

There is no virtualenv. `requirements.txt` pins `Django==5.2.13` and
`python-dotenv==1.2.4`, installed in the system interpreter alongside its own
dependencies. Dev tooling (currently `ruff==0.16.10`) lives in
`requirements-dev.txt`. If you add a package, pin it in one of those files, and
update this section.

`settings.py` calls `load_dotenv(BASE_DIR / '.env')` at import time. `.env` is
gitignored and never committed.

`SECRET_KEY` is read from the `DJANGO_SECRET_KEY` environment variable and no
secret is committed. With `DEBUG = True` and the variable unset, settings fall
back to a throwaway key generated per process, so the commands above work with
no setup — but sessions and password-reset links will not survive a restart.
Set the variable (e.g. in `.env`) for a stable key. With `DEBUG` off, a missing
`DJANGO_SECRET_KEY` raises `ImproperlyConfigured`.

`python manage.py ensure_admin` reads `ADMIN_USER` (default `admin`) and
`ADMIN_PWD` from the environment; both are usually declared in `.env`. It
idempotently creates or updates the superuser, assigning the seeded `admin`
`Role` and re-hashing the password on every run. `migrate` never creates users,
and the local SQLite DB is disposable — re-run `ensure_admin` after any rebuild.

## Conventions

- Function-based views for simple pages; class-based views (`ListView`,
  `CreateView`) for anything with a list/form.
- `path()` and `include()` with `app_name` + named routes. No `re_path()`
  unless a pattern genuinely requires it.
- Every `ModelForm` field is explicit — do not rely on `fields = "__all__"`.
- Templates: `{% extends "base.html" %}` and `{% block %}`. Django 5.2
  template code only; no `{% load staticfiles %}` (removed in 3.0), use
  `{% load static %}`.
- `{% url %}` over hardcoded paths.
- Code, model names, and field names in English (`shift`, `activity`).
  User-facing strings, labels, help_text, and docs in pt-BR.
- Format with Ruff. Config lives in `pyproject.toml` (`[tool.ruff]`); run
  `ruff check --fix` before `ruff format`. Migrations are excluded (generated).
- Migrations **are committed**. Commit the model change and its generated
  migration together, in one commit, per the Django docs. Never add
  `**/migrations/**` back to `.gitignore`.
- `User.role` is deliberately **excluded from `REQUIRED_FIELDS`**. Django's
  `createsuperuser` passes required fields through `Field.clean()`, which
  returns a raw pk, so a `ForeignKey` in `REQUIRED_FIELDS` makes the command
  crash with `ValueError: must be a "Role" instance`. `UserManager`
  assigns the `admin` role instead, and fails loudly (NOT NULL) if it ever
  stops doing so. Do not "fix" this.
- Tests go in `<app>/tests.py` or `<app>/tests/`, named `test_*.py`, classes
  `Test*`/`*TestCase` using `django.test.TestCase`. Write tests alongside any
  model, form, or view you add.

## Boundaries

Never:
- Add a dependency without a `requirements.txt` entry and asking first.
- Run `migrate` against anything but the local `db.sqlite3`.
- Commit `.env`, `local_settings.py`, `db.sqlite3`, or `__pycache__/`.
- Leave a new `SECRET_KEY` in `settings.py`; move it to an env var when you
  touch that file.
- Copy snippets from Django < 4.0 sources (South, `MIDDLEWARE_CLASSES`,
  `urlresolvers`, `render_to_response`, `patterns()`).

Ask first:
- Switching the database engine (the README says SQLite; the Docker deploy
  may change that).
- Adding Django REST Framework, chart libraries, or any UI framework. The
  README's API and chart requirements are unimplemented, so library choice is
  an open decision.

## Definition of done

1. `python manage.py check` passes with no warnings.
2. `python manage.py makemigrations --check` reports no pending changes after
   any model edit.
3. `python manage.py test` passes and actually contains your new test — the
   suite is currently empty, so a green run proves nothing until you add one.
4. `README.md`'s checklist is updated if you finished a roadmap item.
5. This file is updated if you changed a command or convention.
