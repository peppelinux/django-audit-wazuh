import logging

from django.contrib.auth.signals import (user_logged_in,
                                         user_login_failed,
                                         user_logged_out)
from django.dispatch import receiver
from django.conf import settings

from . utils import get_request_info


logger = logging.getLogger(__name__)

USER_FIELD = getattr(settings, 'AUDIT_USERNAME_FIELD', 'username')


@receiver(user_logged_in)
def login_logger(sender, request, **kwargs):
    _msg = '"Django Login successful", "username": "{}", {}'
    logger.info(_msg.format(request.POST[USER_FIELD],
                            get_request_info(request)))


@receiver(user_login_failed)
def login_failed_logger(sender, request, **kwargs):
    _msg = '"Django Login failed", "username": "{}", {}'
    logger.warn(_msg.format(request.POST[USER_FIELD],
                            get_request_info(request)))


@receiver(user_logged_out)
def logout_logger(sender, request, **kwargs):
    _msg = '"Django Logout successful", "username": "{}", {}'
    logger.info(_msg.format(request.user,
                            get_request_info(request)))
