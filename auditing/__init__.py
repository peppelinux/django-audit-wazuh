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

    def get_username_in(credentials: dict):
        """
        Find the username in credentials dict based on list of valid username
        keys.
        """
        USER_FIELDS = getattr(settings, 'AUDIT_USERNAME_FIELDS', ['username'])
        for key in USER_FIELDS:
            if key in credentials.keys():
                return credentials[key]
        raise KeyError("Valid username not found in credentials.")

    msg_data = get_request_info(kwargs['request'])
    msg_data['username'] = get_username_in(kwargs['credentials'])
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
