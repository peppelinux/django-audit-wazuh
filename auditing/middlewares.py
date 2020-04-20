import logging
import re

from django.conf import settings
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

logger = logging.getLogger(__name__)


AUDITING_REQUEST_RESPONSE_KEYS_REGEX = getattr(settings,
                                               'AUDITING_REQUEST_RESPONSE_KEYS_REGEX',
                                               r'(HTTP_COOKIE|HTTP_USER_|SERVER_NAME|CSRF_|QUERY_|REMOTE_)')
AUDIT_RESPONSE_HTTPCODES = getattr(settings,
                                   'AUDIT_RESPONSE_HTTPCODES',
                                   (400,401,402,403,404,500,501,502,503))
AUDIT_REQUEST_POST_IGNORED = ('password', )


class HttpHeadersLoggingMiddleware(MiddlewareMixin):
    
    def process_response(self, request, response):
        # request
        keys = sorted(filter(lambda k: re.match(AUDITING_REQUEST_RESPONSE_KEYS_REGEX, k), request.META))
        meta = ', '.join("%s=%s" % (k, request.META[k]) for k in keys)
        logger.debug(meta)

        # request.POST
        if request.POST:
            _msg = ', '.join(('{}: {}'.format(k,v) for k,v in request.POST.items() if k not in AUDIT_REQUEST_POST_IGNORED))
            logger.debug('HTTP Request POST: {}'.format(_msg))
        if request.GET:
            _msg = ', '.join(('{}: {}'.format(k,v) for k,v in request.GET.items()))
            logger.debug('HTTP Request GET: {}'.format(_msg))
        
        # response
        status_text = 'STATUS CODE'
        if response.status_code in AUDIT_RESPONSE_HTTPCODES:
            logger.error('{}: {}'.format(status_text, response.status_code))

        status = '{} {}'.format(response.status_code, status_text)
        response_headers = [(str(k), str(v)) for k, v in response.items()]
        for c in response.cookies.values():
            response_headers.append(('Set-Cookie', str(c.output(header=''))))
        head_items = ["{}: {}".format(*hea) for hea in response_headers]
        headers = ', '.join(head_items)
        logging.debug('{} {} - {} - {} - {}'.format(request.method,
                                                    request.build_absolute_uri(), meta,
                                                    status, headers))
        return response
