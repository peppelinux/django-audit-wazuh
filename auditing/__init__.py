import logging

from django.contrib.auth.signals import (user_logged_in,
                                         user_login_failed,
                                         user_logged_out)
from django.dispatch import receiver
from django.conf import settings

from .utils import get_request_info, format_log_message


logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def login_logger(sender, **kwargs):
    msg_data = get_request_info(kwargs['request'])
    msg_data['username'] = kwargs['user'].get_username()
    logger.info('"Django Login successful", {}'.format(
        format_log_message(msg_data)))


@receiver(user_login_failed)
def login_failed_logger(sender, **kwargs):
    USER_FIELD = getattr(settings, 'AUDIT_USERNAME_FIELD', 'username')
    msg_data = get_request_info(kwargs['request'])
    msg_data['username'] = kwargs['credentials'][USER_FIELD]
    logger.warn('"Django Login failed", {}'.format(
        format_log_message(msg_data)))


@receiver(user_logged_out)
def logout_logger(sender, **kwargs):
    msg_data = get_request_info(kwargs['request'])
    user = kwargs.get('user', None)

    if user is not None:
        msg_data['username'] = user.get_username()
        logger.info('"Django Logout successful", {}'.format(
            format_log_message(msg_data)))
    else:
        logger.debug('"Django Logout failed", {}'.format(
            format_log_message(msg_data)))
