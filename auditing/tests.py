import json
from unittest.mock import Mock

from django import http
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from .middleware import http_headers_logging_middleware
from .utils import get_request_info, format_log_message
from . import login_logger, login_failed_logger, logout_logger


class GetRequestInfoTestCase(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def test_returns_dict(self):
        request = self.rf.get('/login/')
        req_data = get_request_info(request)

        self.assertIsInstance(req_data, dict)

    def test_msg_data(self):
        request = self.rf.get('/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        req_data = get_request_info(request)

        self.assertDictEqual(req_data, {
            'Cookie': '',
            'path': '/login/',
            'url': 'http://testserver/login/',
            'srcip': '127.0.0.1',
        })

    def test_xforward_for(self):
        request = self.rf.get('/login/', HTTP_X_FORWARDED_FOR='127.1.1.1')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        req_data = get_request_info(request)

        self.assertDictEqual(req_data, {
            'Cookie': '',
            'X-Forwarded-For': '127.1.1.1',
            'path': '/login/',
            'url': 'http://testserver/login/',
            'srcip': '127.1.1.1',
        })

    def test_xreal_ip(self):
        request = self.rf.get('/login/', HTTP_X_REAL_IP='127.2.2.2')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        req_data = get_request_info(request)

        self.assertDictEqual(req_data, {
            'Cookie': '',
            'X-Real-Ip': '127.2.2.2',
            'path': '/login/',
            'url': 'http://testserver/login/',
            'srcip': '127.2.2.2',
        })


class FormatMessageTestCase(TestCase):
    """
    Test cases for the `format_log_message` function
    """
    MSG_DATA = {
        "Cookie": "",
        "path": "/login/",
        "url": "http://testserver/login/",
        "srcip": "127.0.0.1",
    }

    def test_returns_valid_json_with_brackets(self):
        msg = format_log_message(self.MSG_DATA)
        try:
            json.loads('{' + msg + '}')
        except json.decoder.JSONDecodeError:
            self.fail("Message string is not valid JSON")

    def test_returns_string_without_brackets(self):
        msg = format_log_message(self.MSG_DATA)
        self.assertNotEqual(msg[0], '{')
        self.assertNotEqual(msg[-1], '}')
        self.assertEqual(
            msg,
            '"Cookie": "", '
            '"path": "/login/", '
            '"url": "http://testserver/login/", '
            '"srcip": "127.0.0.1"')


class MockUser(object):
    """
    Create a mock user that we can use in our signals.
    We only need it to have the `get_username` method that the django
    user model has.
    """
    def __init__(self, username='tester'):
        self.username = username

    def get_username(self):
        return self.username


class SignalsBaseTestCase(TestCase):
    """
    A base class that covers some common functionality for signal tests.
    """
    def setUp(self):
        self.mock_sender = Mock()
        self.user = MockUser()

    def _post(self, path='/login/', data=None):
        """
        Uses the request factory to create a post response
        """
        if data is None:
            data = {
                'username': 'tester',
                'password': 'secret',
            }
        rf = RequestFactory()
        return rf.post(path, data)


class LoginLoggerReceiverTestCase(SignalsBaseTestCase):

    def test_message_result(self):
        req = self._post()

        with self.assertLogs('auditing', level='INFO') as cm:
            login_logger(self.mock_sender, user=MockUser(), request=req)

        out = cm.output[0]

        self.assertIn('INFO:auditing:"Django Login successful"', out)
        self.assertIn('"Cookie": ""', out)
        self.assertIn('"path": "/login/"', out)
        self.assertIn('"url": "http://testserver/login/"', out)
        self.assertIn('"srcip": "127.0.0.1"', out)
        self.assertIn('"username": "tester"', out)

    def test_ignored_fields(self):
        req = self._post(data={
            'username': 'tester',
            'password': 'secret',
            'password1': 'secret',
            'password2': 'secret',
        })

        with self.assertLogs('auditing', level='INFO') as cm:
            login_logger(self.mock_sender, user=MockUser(), request=req)

        out = cm.output[0]

        self.assertIn('"username": "tester"', out)
        self.assertNotIn('"password":', out)
        self.assertNotIn('"password1":', out)
        self.assertNotIn('"password2":', out)

    @override_settings(AUDIT_USERNAME_FIELD='email')
    def test_message_custom_user_field(self):
        req = self._post(data={
            "email": "user@example.com",
            "password": "secret",
        })

        with self.assertLogs('auditing', level='INFO') as cm:
            login_logger(
                self.mock_sender,
                user=MockUser(username='user@example.com'),
                request=req)

        self.assertIn('"username": "user@example.com"', cm.output[0])


class LoginFailedLoggerReceiverTestCase(SignalsBaseTestCase):

    def test_message_result(self):
        req = self._post()

        with self.assertLogs('auditing', level='INFO') as cm:
            login_failed_logger(
                self.mock_sender,
                # Django obfuscatesthe password in this signal, so we simulate
                # that here also
                credentials={'username': 'wrong', 'password': '***********'},
                request=req)

        out = cm.output[0]

        self.assertIn('WARNING:auditing:"Django Login failed"', out)
        self.assertIn('"Cookie": ""', out)
        self.assertIn('"path": "/login/"', out)
        self.assertIn('"url": "http://testserver/login/"', out)
        self.assertIn('"srcip": "127.0.0.1"', out)
        self.assertIn('"username": "wrong"', out)

    def test_ignored_fields(self):
        req = self._post(data={
            'username': 'tester',
            'password': 'secret',
            'password1': 'secret',
            'password2': 'secret',
        })

        with self.assertLogs('auditing', level='INFO') as cm:
            login_failed_logger(
                self.mock_sender,
                credentials={'username': 'wrong', 'password': '***********'},
                request=req)

        out = cm.output[0]

        self.assertIn('"username": "wrong"', out)
        self.assertNotIn('"password": ', out)
        self.assertNotIn('"password1": ', out)
        self.assertNotIn('"password2": ', out)

    @override_settings(AUDIT_USERNAME_FIELD='email')
    def test_message_custom_user_field(self):
        req = self._post(data={
            "email": "user@example.com",
            "password": "secret",
        })

        with self.assertLogs('auditing', level='INFO') as cm:
            login_failed_logger(
                self.mock_sender,
                credentials={'email': 'wrong', 'password': '************'},
                request=req)

        self.assertIn('"username": "wrong"', cm.output[0])


class LogoutLoggerReceiverTestCase(SignalsBaseTestCase):

    def test_message_result(self):
        req = self._post()

        with self.assertLogs('auditing', level='INFO') as cm:
            logout_logger(self.mock_sender, user=MockUser(), request=req)

        out = cm.output[0]

        self.assertIn('INFO:auditing:"Django Logout successful"', out)
        self.assertIn('"Cookie": ""', out)
        self.assertIn('"path": "/login/"', out)
        self.assertIn('"url": "http://testserver/login/"', out)
        self.assertIn('"srcip": "127.0.0.1"', out)
        self.assertIn('"username": "tester"', out)

    def test_logout_refresh_by_user(self):
        """
        It's possible that a user can refresh the logout page. This will cause
        the signal to fire again and we need to test that this doesn't raise
        errors because the user will be None in this case.
        """
        req = self._post()

        with self.assertLogs('auditing', level='DEBUG') as cm:
            logout_logger(self.mock_sender, user=None, request=req)

        self.assertIn('DEBUG:auditing:"Django Logout failed"', cm.output[0])

    def test_ignored_fields(self):
        req = self._post(data={
            'username': 'tester',
            'password': 'secret',
            'password1': 'secret',
            'password2': 'secret',
        })

        with self.assertLogs('auditing', level='INFO') as cm:
            logout_logger(self.mock_sender, user=MockUser(), request=req)

        out = cm.output[0]

        self.assertIn('"username": "tester"', out)
        self.assertNotIn('"password":', out)
        self.assertNotIn('"password1":', out)
        self.assertNotIn('"password2":', out)

    @override_settings(AUDIT_USERNAME_FIELD='email')
    def test_message_custom_user_field(self):
        req = self._post(data={
            "email": "user@example.com",
            "password": "secret",
        })

        with self.assertLogs('auditing', level='INFO') as cm:
            logout_logger(
                self.mock_sender,
                user=MockUser('user@example.com'),
                request=req)

        self.assertIn('"username": "user@example.com"', cm.output[0])


class HTTPHeadersLoggingMiddlewareTestCase(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def test_middleware_get_request(self):
        request = self.rf.get('/')

        middleware = http_headers_logging_middleware(
            lambda r: http.HttpResponse('200 Success'))

        with self.assertLogs('auditing', level='DEBUG') as cm:
            response = middleware(request)

        # Verify that 1 log entry was generated
        self.assertEqual(1, len(cm.output))
        self.assertIn('DEBUG:auditing.middleware:"Http Response"', cm.output[0])

    def test_post_request(self):
        request = self.rf.post('/', {
            "email": "user@example.com",
            "password": "secret",
        })

        middleware = http_headers_logging_middleware(
            lambda r: http.HttpResponseRedirect('/success/'))

        with self.assertLogs('auditing', level='DEBUG') as cm:
            response = middleware(request)

        self.assertEqual(2, len(cm.output))
        self.assertIn('"Http Request POST",', cm.output[0])
        self.assertNotIn('"password"', cm.output[0])

    def test_important_status_codes_get(self):
        request = self.rf.get('/')

        middleware = http_headers_logging_middleware(
            lambda r: http.HttpResponseForbidden())

        with self.assertLogs('auditing', level='ERROR') as cm:
            response = middleware(request)

        self.assertIn('"Http Response",', cm.output[0])
        self.assertIn('"status": 403', cm.output[0])

    def test_important_status_codes_post(self):
        request = self.rf.post('/', {
            "email": "user@example.com",
            "password": "secret",
        })

        middleware = http_headers_logging_middleware(
            lambda r: http.HttpResponseForbidden('/'))

        with self.assertLogs('auditing', level='ERROR') as cm:
            response = middleware(request)

        self.assertIn('"Http Response",', cm.output[0])
        self.assertIn('"status": 403', cm.output[0])

        # Since it was a post message, check that these were included
        self.assertIn('"post": {', cm.output[0])
        self.assertIn('"email": "user@example.com"', cm.output[0])

        # Sensitive info should still be stripped
        self.assertNotIn('"password"', cm.output[0])
