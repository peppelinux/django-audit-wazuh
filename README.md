django-audit
------------

Auditing app, simple as possible, to have a good logging system for security purpose.
You'll have a json file abe to be processed by a SIEM like Wazuh.

Setup
-----

````
pip install git+https://github.com/peppelinux/django-audit.git
````

Configuration
-------------

In `settings.py`:

1. add 'auditing' in `INSTALLED_APPS`
2. add a Middleware as follows
3. configure a logging as follows

````
# requests headers auditing
if 'auditing' in INSTALLED_APPS:
    MIDDLEWARE.append('auditing.middlewares.HttpHeadersLoggingMiddleware')
#

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s] %(message)s [(%(levelname)s)] %(args)s %(name)s %(filename)s.%(funcName)s:%(lineno)s]'
        },
        'json': {
            'format': '{"date": "%(asctime)s", "msg": "%(message)s", "level": "%(levelname)s",  "name": "%(name)s", "path": "%(filename)s.%(funcName)s:%(lineno)s"}'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'formatter': 'json',
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './django_siem.log',
        },
        'console': {
            'formatter': 'detailed',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        
        
    },
    'loggers': {
        'django.security': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.contrib.auth': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'auditing': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

````

Results
-------

You'll get a file with all the relevant events in json format, like

````
{"date": "2020-04-20 13:20:00,794", "msg": "Login failed for "adad", next: "/gestione"", "level": "WARNING",  "name": "auditing", "path": "__init__.py.login_failed_logger:22"}
{"date": "2020-04-20 13:20:01,517", "msg": "STATUS CODE: 404", "level": "ERROR",  "name": "auditing.middlewares", "path": "middlewares.py.process_response:41"}
{"date": "2020-04-20 13:20:01,521", "msg": "Not Found: /favicon.ico", "level": "WARNING",  "name": "django.request", "path": "log.py.log_response:228"}
{"date": "2020-04-20 13:20:45,126", "msg": "Login failed for "adad", next: "/gestione"", "level": "WARNING",  "name": "auditing", "path": "__init__.py.login_failed_logger:22"}
{"date": "2020-04-20 13:20:52,406", "msg": "Login succesfull for "wert", next: "/gestione"", "level": "INFO",  "name": "auditing", "path": "__init__.py.login_logger:15"}
{"date": "2020-04-20 13:20:55,846", "msg": "Logout succesfull for "wert"", "level": "INFO",  "name": "auditing", "path": "__init__.py.logout_logger:28"}
````
