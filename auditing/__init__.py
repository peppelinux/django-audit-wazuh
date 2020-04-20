import logging

from django.contrib.auth.signals import (user_logged_in,
                                         user_login_failed,
                                         user_logged_out)
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def login_logger(sender, request, **kwargs):
    _msg = 'Login succesfull for "{}", next: "{}"'
    logger.info(_msg.format(request.POST['username'],
                            request.POST['next']))


@receiver(user_login_failed)
def login_failed_logger(sender, request, **kwargs):
    _msg = 'Login failed for "{}", next: "{}"'
    logger.warn(_msg.format(request.POST['username'],
                            request.POST['next']))


@receiver(user_logged_out)
def logout_logger(sender, request, **kwargs):
    _msg = 'Logout succesfull for "{}"'
    logger.info(_msg.format(request.user))
