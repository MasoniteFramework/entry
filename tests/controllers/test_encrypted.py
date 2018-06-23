from entry.api.controllers import EncryptedGrantController

from masonite.request import Request
from masonite.app import App
from masonite.testsuite.TestSuite import generate_wsgi

class MockAuth:
    def __init__(self, *args):
        pass

    def login(self, *args):
        return self

class TestJwtController:

    def setup_method(self):
        self.app = App()
        self.request = Request(generate_wsgi())
        self.controller = EncryptedGrantController()
    
    def test_generating_key_returns_user_and_password_required(self):
        assert self.controller.generate(self.request)['error']
    
    def test_controller_generates_secret_key(self):
        self.request.request_variables = {'username': 'test', 'password': 'test'}
        self.controller.__auth__ = MockAuth
        assert self.controller.generate(self.request)['token']
    
    def test_refresh_generates_new_token(self):
        self.request.request_variables = {'username': 'test', 'password': 'test'}
        self.controller.__auth__ = MockAuth
        token = self.controller.generate(self.request)
        self.request.request_variables = {'token': token['token']}

        assert self.controller.refresh(self.request)['token'] != token