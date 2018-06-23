from entry.api.controllers import OAuth2Controller
from masonite.request import Request
from masonite.app import App
from masonite.testsuite.TestSuite import generate_wsgi
from masonite.view import View

class MockApplication:
    KEY = 'NCTpkICMlTXie5te9nJniMj9aVbPM6lsjeq5iDZ0dqY='

class MockApplicationModel:

    name = 'Masonite Application'
    description = 'Test Description'

    def where(self, column, value):
        setattr(self, column, value)
        return self
    
    def first(self):
        return self

class TestController:

    def setup(self):
        self.app = App()
        self.app.bind('Application', MockApplication)
        self.request = Request(generate_wsgi()).load_app(self.app)
        self.view = View(self.app)

    def test_controller_return_requires_username(self):
        assert OAuth2Controller().generate(self.request)['error']
    
    def test_controller_signs_payload_with_username_and_password(self):
        self.request.request_variables = {'username': 'test@email.com', 'password': 'secret'}
        controller = OAuth2Controller()
        controller.__application__ = MockApplicationModel()


        controller.show(self.request, self.view)
        # assert OAuth2Controller().generate(self.request)['authorization_code']
    
