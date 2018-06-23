from entry.api.controllers import OAuth2Controller
from masonite.request import Request
from masonite.app import App
from masonite.testsuite.TestSuite import generate_wsgi
from masonite.view import View
import pendulum

class MockApplication:
    KEY = 'NCTpkICMlTXie5te9nJniMj9aVbPM6lsjeq5iDZ0dqY='

class MockApplicationModel:

    name = 'Masonite Application'
    description = 'Test Description'
    client_id = '1234'
    client_secret = '1234-test'

    def where(self, column, value):
        setattr(self, column, value)
        return self
    
    def first(self):
        return self

class MockTokenModel:

    scopes = ['user:read']
    refresh_expires_at = pendulum.now().add(minutes=5)

    def where(self, column, value):
        setattr(self, column, value)
        return self
    
    def create(self, *args, **kwargs):
        return self
    
    def first(self):
        return self

    def save(self):
        return self

class MockRequstWithUser:

    def user(self):
        self.id = 1
        return self

class TestController:

    def setup(self):
        self.app = App()
        self.app.bind('Application', MockApplication)
        self.request = Request(generate_wsgi()).load_app(self.app)
        self.view = View(self.app)
        self.controller = OAuth2Controller
        self.controller.__application__ = MockApplicationModel()
        self.controller.__token__ = MockTokenModel()
    
    def test_controller_returns_view(self):
        self.request.request_variables = {'username': 'test@email.com', 'password': 'secret'}

        assert self.controller().show(self.request, self.view)
        # assert OAuth2Controller().generate(self.request)['authorization_code']
    
    def test_controller_signs_payload_with_username_and_password(self):
        self.request.request_variables = {
            'redirect_uri': 'http://test.com' 
        }

        self.request.extend(MockRequstWithUser)

        assert self.controller().send(self.request)
        assert self.request.redirect_url.startswith('http://test.com?code=')

    def test_controller_authorizes_application(self):
        self.request.request_variables = {
            'redirect_uri': 'http://test.com' 
        }

        assert self.controller().authorize(self.request)

    def test_controller_returns_wrong_grant_type(self):
        self.request.request_variables = {
            'redirect_uri': 'http://test.com' 
        }

        assert self.controller().refresh(self.request)['error']

    def test_controller_returns_wrong_grant_type(self):
        self.request.request_variables = {
            'redirect_uri': 'http://test.com' 
        }

        assert self.controller().refresh(self.request)['error']

    def test_controller_returns_new_token(self):
        self.request.request_variables = {
            'refresh_token': '1234',
            'grant_type': 'refresh_token'
        }

        assert self.controller().refresh(self.request)['access_token']