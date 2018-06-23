''' Database Settings '''

import os
import json

from entry.api.Resource import Resource
from entry.api import JsonSerialize
from entry.api.auth import OAuth2
from entry.api.exceptions import NoApiTokenFound, ExpiredToken, PermissionScopeDenied
from entry.api.controllers import JWTGrantController
from masonite.app import App
from masonite.request import Request
from masonite.testsuite.TestSuite import generate_wsgi
import pytest
import pendulum


class EntryTest:
    __table__ = 'entry_test'
    __fillable__ = ['name']
    __timestamps__ = False

    def all(self):
        return {'test': 'test'}

class TokenModel:

    scopes = ''
    expires_at = str(pendulum.now().add(minutes=5))

    def where(self, column, value):
        return self
    
    def first(self):
        return self

class EntryTestResource(Resource, JsonSerialize, OAuth2):
    model = EntryTest
    url = '/api/entrytest'
    data_wrap = False
    expires_in = '5 minutes'
    token_model = TokenModel

REQUEST = Request(generate_wsgi())

class TestEncryptedAuthentication:

    def setup_method(self):
        self.app = App()
        self.request = REQUEST.load_app(self.app)
        self.auth = OAuth2()
        self.auth.token_model = TokenModel()

    def test_auth_throws_no_api_token_error(self):
        self.auth.request = self.request
        with pytest.raises(NoApiTokenFound):
            assert self.auth.authenticate()
    
    def test_auth_throws_error_on_no_token(self):
        self.request.request_variables = {'token': 'token'}
        self.auth.request = self.request
        assert self.auth.authenticate() is None
    
    def test_auth_throws_error_on_expired_token(self):
        self.request.request_variables = {'token': 'token'}
        self.auth.request = self.request
        self.auth.token_model.expires_at = pendulum.now().subtract(minutes=5)

        with pytest.raises(ExpiredToken):
            assert self.auth.authenticate()

    def test_auth_exception_incorrect_permission_scope(self):
        self.request.request_variables = {'token': 'test-token', 'scope': 'user:read'}
        self.auth.request = self.request
        self.auth.scopes = 'user:post'

        with pytest.raises(PermissionScopeDenied):
            assert self.auth.authenticate()
        
