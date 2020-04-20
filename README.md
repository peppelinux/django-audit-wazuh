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
            'format': '{"date": "%(asctime)s", "msg": "%(message)s", "level": "%(levelname)s",  "name": "%(name)s", "path": "%(filename)s.%(funcName)s:%(lineno)s", "@source":"django-audit"}'
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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './django_siem.log',
            'maxBytes': 1024000,
            'backupCount': 3,
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
{"date": "2020-04-20 15:43:16,089", "msg": "Login failed for "asdfs", next: "/gestione", request: PATH: /gestionelogin/?next=/gestione - HEADERS: Content-Length=130,Content-Type=application/x-www-form-urlencoded,Host=localhost:8000,User-Agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0,Accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8,Accept-Language=en-US,en;q=0.5,Accept-Encoding=gzip, deflate,Origin=http://localhost:8000,Connection=keep-alive,Referer=http://localhost:8000/gestionelogin/?next=/gestione,Cookie=csrftoken=reF5MTMlP3d1QSNsCHZvw4NuUAbxSytAdRPv9olRfFdYSttsvM3YU7tVKHam6OOt; cookieconsent_status=dismiss; session=eyJvcF9oYXNoIjoiZGphbmdvX29pZGNfb3AifQ.XpxTJA.hqdgNaC8h_p_iwihldXJgrdjwRk,Upgrade-Insecure-Requests=1", "level": "WARNING",  "name": "auditing", "path": "__init__.py.login_failed_logger:25", "@source":"django-audit"}
{"date": "2020-04-20 15:43:54,283", "msg": "STATUS CODE 404,  - PATH: /gsadasd - HEADERS: Content-Type=text/plain,Host=localhost:8000,User-Agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0,Accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8,Accept-Language=en-US,en;q=0.5,Accept-Encoding=gzip, deflate,Connection=keep-alive,Cookie=csrftoken=reF5MTMlP3d1QSNsCHZvw4NuUAbxSytAdRPv9olRfFdYSttsvM3YU7tVKHam6OOt; cookieconsent_status=dismiss; session=eyJvcF9oYXNoIjoiZGphbmdvX29pZGNfb3AifQ.XpxTJA.hqdgNaC8h_p_iwihldXJgrdjwRk,Upgrade-Insecure-Requests=1", "level": "ERROR",  "name": "auditing.middlewares", "path": "middlewares.py.process_response:48", "@source":"django-audit"}
````

Tuning
------

Auditing Middleware can log everything between a http request and its following response.
These are the overloadable settings variables

````
# for i in http.HTTPStatus: print(i, i.value) 
AUDIT_RESPONSE_HTTPCODES = getattr(settings,
                                   'AUDIT_RESPONSE_HTTPCODES',
                                   [i.value for i in http.HTTPStatus if i not in (200,201,202,301,302)])

# prevents to read the password in clear
AUDIT_REQUEST_POST_IGNORED = ('password', )
````


Wazuh configuration
-------------------

1. copy the content of `wazuh-ruleset/27081-django_rules.xml` in `/var/ossec/etc/rules/local_rules.xml`
