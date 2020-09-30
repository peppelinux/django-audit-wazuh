import logging
import json

from django.conf import settings
from . utils import get_request_info, format_log_message


logger = logging.getLogger(__name__)


# AUDITING_REQUEST_RESPONSE_KEYS_REGEX = getattr(settings,
#                                                'AUDITING_REQUEST_RESPONSE_KEYS_REGEX',
#                                                r'(HTTP_COOKIE|HTTP_USER_|SERVER_NAME|CSRF_|QUERY_|REMOTE_)')

# Assume all codes, and only remove or ignore the ones that are not to be
# analyzed
AUDIT_RESPONSE_STATUS_IGNORED = getattr(settings,
                                        'AUDIT_RESPONSE_STATUS_IGNORED',
                                        (200, 201, 202, 301, 302))

AUDIT_REQUEST_POST_IGNORED = getattr(settings,
                                     'AUDIT_REQUEST_POST_IGNORED',
                                     ('password', 'password1', 'password2'))


def http_headers_logging_middleware(get_response):

    def middleware(request):
        msg_data = get_request_info(request)

        # Remove any sensitive POST data that we don't want in the logs
        if request.method == 'POST':
            post_data = request.POST.copy()
            for k in AUDIT_REQUEST_POST_IGNORED:
                post_data.pop(k, None)
            msg_data['post'] = post_data

            msg = '"Http Request POST", {}'.format(format_log_message(msg_data))
            logger.debug(msg)

        resp = get_response(request)

        if resp.status_code not in AUDIT_RESPONSE_STATUS_IGNORED:
            msg_data['status'] = resp.status_code
            msg = '"Http Response", {}'.format(format_log_message(msg_data))
            logger.error(msg)

        # Add response headers to data
        msg_data.update(resp.items())

        # Add response cookies
        msg_data['Resp-Cookies'] = resp.cookies.output()

        # Finally create a debug log message
        msg_data.update({
            'method': request.method,
            'status': resp.status_code,
        })

        msg = '"Http Response", {}'.format(format_log_message(msg_data))
        logger.debug(msg)

        return resp

    return middleware
