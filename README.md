Django Audit Wazuh
------------------

Auditing app, simple as possible, to have a good logging system for security purpose.
You'll have a json file able to be processed by a SIEM like Wazuh or OSSEC.

Features
- Login, logout and bruteforce attempts.

Todo
- Other critical django.security messages, needs more testing with sane unit tests.

Setup
-----

````
pip install django-audit-wazuh
# or
pip install git+https://github.com/peppelinux/django-audit-wazuh.git
````

Configuration
-------------

In `settings.py`:

1. add 'auditing' in `INSTALLED_APPS`
2. add a Middleware as follows (not mandatory!)
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
            'format': '{"timestamp": "%(asctime)s", "msg": %(message)s, "level": "%(levelname)s",  "name": "%(name)s", "path": "%(filename)s.%(funcName)s:%(lineno)s", "@source":"django-audit"}'
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
{"timestamp": "2020-04-21 13:05:01,238", "msg": "Django Login failed", "username": "dsfsdf", "url": "http://localhost:8000/gestionelogin/?next=/gestione", "data.srcip": "127.0.0.1", "path": "/gestionelogin/?next=/gestione", "Content-Length": "132", "Content-Type": "application/x-www-form-urlencoded", "Host": "localhost:8000", "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Origin": "http://localhost:8000", "Connection": "keep-alive", "Referer": "http://localhost:8000/gestionelogin/?next=/gestione", "Cookie": "csrftoken=pTG3UCHtiE0q4PNectVIH4hbezbqL2O2tvWx97rY8zwOxigSzG9unl2tqELzMhpM; cookieconsent_status=dismiss", "Upgrade-Insecure-Requests": "1", "level": "WARNING",  "name": "auditing", "path": "__init__.py.login_failed_logger:23", "@source":"django-audit"}
{"timestamp": "2020-04-21 13:05:33,521", "msg": "Django Login successful", "username": "wert", "url": "http://localhost:8000/gestionelogin/?next=/gestione", "data.srcip": "127.0.0.1", "path": "/gestionelogin/?next=/gestione", "Content-Length": "131", "Content-Type": "application/x-www-form-urlencoded", "Host": "localhost:8000", "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Origin": "http://localhost:8000", "Connection": "keep-alive", "Referer": "http://localhost:8000/gestionelogin/?next=/gestione", "Cookie": "csrftoken=pTG3UCHtiE0q4PNectVIH4hbezbqL2O2tvWx97rY8zwOxigSzG9unl2tqELzMhpM; cookieconsent_status=dismiss", "Upgrade-Insecure-Requests": "1", "level": "INFO",  "name": "auditing", "path": "__init__.py.login_logger:16", "@source":"django-audit"}
{"timestamp": "2020-04-21 13:05:36,582", "msg": "Django Logout successful", "username": "wert", "url": "http://localhost:8000/gestionelogout/", "data.srcip": "127.0.0.1", "path": "/gestionelogout/", "Content-Type": "text/plain", "Host": "localhost:8000", "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "keep-alive", "Referer": "http://localhost:8000/gestione", "Cookie": "csrftoken=e50mIQ4NWKYjDKBKA9a1iFufQuRv2W8LKAWnIjm4meXhiCSWPHzxfkrllMeNVqDR; cookieconsent_status=dismiss; sessionid=cxu3hfono6t6p1dl70q80836pe292ri3", "Upgrade-Insecure-Requests": "1", "level": "INFO",  "name": "auditing", "path": "__init__.py.logout_logger:30", "@source":"django-audit"}
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

1. Copy the content of `wazuh-ruleset/27081-django_decoders.xml` in `/var/ossec/etc/decoders/local_decoder.xml`

2. Copy the content of `wazuh-ruleset/27081-django_rules.xml` in `/var/ossec/etc/rules/local_rules.xml`.

3. Test the triggers with `/var/ossec/bin/ossec-logtest`, copy a log line in stdin and see events.

4. Create an agent group called `django`
   ````
   /var/ossec/bin/agent_groups -a -g django
   ````
5. Edit agent group configuration `/var/ossec/etc/shared/django/agent.conf` this way
   ````
   <localfile>
        <location>ABSOLUTE_PATH_TO_YOUR_DJANGO_AUDIT_LOG.json</location>
        <log_format>json</log_format>
        <label key="@source">django-audit</label>
   </localfile>
   ````
6. Add agents to this group
   ````
   /var/ossec/bin/agent_groups -a -i 014 -g django
   ````
7. Control when they are synced
   ````
   /var/ossec/bin/agent_groups -S -i 014
   ````
8. Restart Wazuh-manager to reload rulesets `service wazuh-manager restart`


GeoIP
-----

On wazuh-manager, edit /usr/share/filebeat/module/wazuh/alerts/ingest/pipeline.json adding the new IP field inside processors, along the other Geolocation fields:
````
    {
      "geoip": {
        "field": "srcip",
        "target_field": "GeoLocation",
        "properties": ["city_name", "country_name", "region_name", "location"],
        "ignore_missing": true,
        "ignore_failure": true
      }
    },
````

We now need to delete the current pipeline. In Kibana, go to Dev Tools clicking on the Wrench icon. Then execute the following:
````
DELETE _ingest/pipeline/filebeat-7.6.2-wazuh-alerts-pipeline
````

We restart Filebeat in wazuh-manager:
````
systemctl restart filebeat
````

License
-------

Apache


Authors
-------

Giuseppe De Marco <giuseppe.demarco@unical.it>


Credits
-------

Garrlab Wazuh SIEM crew
