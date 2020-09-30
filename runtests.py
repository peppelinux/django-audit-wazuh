#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.core.management import call_command


_TEST_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },

    'INSTALLED_APPS': (
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sites',
        'django.contrib.sessions',
        'auditing',
    ),

    'ROOT_URLCONF': '',

    'MIDDLEWARE_CLASSES': (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'auditing.middlewares.http_headers_logging_middleware',
    ),

    'TEMPLATES': [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
}


def runtests():
    if not settings.configured:
        settings.configure(**_TEST_SETTINGS)

    if django.VERSION >= (2, 1):
        django.setup()

    failures = call_command(
        'test',
        'auditing',
        interactive=False,
        failfast=False,
        verbosity=2)

    sys.exit(bool(failures))


if __name__ == '__main__':
    runtests()
