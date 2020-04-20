import logging

from django.contrib.auth.signals import (user_logged_in,
                                         user_login_failed,
                                         user_logged_out)
from django.dispatch import receiver
from . utils import get_request_info

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def login_logger(sender, request, **kwargs):
    _msg = 'Login succesfull for "{}", next: "{}", request: {}'
    logger.info(_msg.format(request.POST['username'],
                            request.POST['next'],
                            get_request_info(request)))


@receiver(user_login_failed)
def login_failed_logger(sender, request, **kwargs):
    _msg = 'Login failed for "{}", next: "{}", request: {}'
    logger.warn(_msg.format(request.POST['username'],
                            request.POST['next'],
                            get_request_info(request)))


@receiver(user_logged_out)
def logout_logger(sender, request, **kwargs):
    _msg = 'Logout succesfull for "{}"'
    logger.info(_msg.format(request.user))
