import http
import logging
import re

from django.conf import settings
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object
from . utils import get_request_info

logger = logging.getLogger(__name__)


#AUDITING_REQUEST_RESPONSE_KEYS_REGEX = getattr(settings,
                                               #'AUDITING_REQUEST_RESPONSE_KEYS_REGEX',
                                               #r'(HTTP_COOKIE|HTTP_USER_|SERVER_NAME|CSRF_|QUERY_|REMOTE_)')
# for i in http.HTTPStatus: print(i, i.value) 
AUDIT_RESPONSE_HTTPCODES = getattr(settings,
                                   'AUDIT_RESPONSE_HTTPCODES',
                                   [i.value for i in http.HTTPStatus if i not in (200,201,202,301,302)] )
AUDIT_REQUEST_POST_IGNORED = ('password', )


class HttpHeadersLoggingMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        # request
        _msg_path_head = get_request_info(request)
        #logger.debug(_msg_path_head)
        
        _msg_post, _msg_get = '',''
        # request.POST
        if request.POST:
            _things = ('{}={}'.format(k,v)
                       for k,v in request.POST.items()
                       if k not in AUDIT_REQUEST_POST_IGNORED)
            _msg_post = ('HTTP Request POST: '
                         ', '.join(_things) + _msg_path_head)
            logger.debug(_msg_post)
        
        # response
        status_text = 'STATUS CODE'
        if response.status_code in AUDIT_RESPONSE_HTTPCODES:
            logger.error('{} {}, {} - {}'.format(status_text,
                                                 response.status_code,
                                                 _msg_post,
                                                 _msg_path_head))
        status = '{} {}'.format(response.status_code, status_text)
        response_headers = [(str(k), str(v)) for k, v in response.items()]
        for cookie in response.cookies.values():
            response_headers.append(('Set-Cookie', str(cookie.output(header=''))))
        head_items = ["{}: {}".format(*hea) for hea in response_headers]
        headers = ', '.join(head_items)
        logging.debug('{} {} - {} - {}'.format(request.method,
                                               request.build_absolute_uri(),
                                               status, headers))
        return response
