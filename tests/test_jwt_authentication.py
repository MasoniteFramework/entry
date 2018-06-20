''' Database Settings '''

import os
import json

from dotenv import find_dotenv, load_dotenv
from orator import DatabaseManager, Model
from entry.api.Resource import Resource
from entry.api.JsonSerialize import JsonSerialize
from entry.api.JWTAuthentication import JWTAuthentication
from entry.entry_snippets.controllers.JWTGrantController import JWTGrantController
from masonite.app import App
from masonite.request import Request
from masonite.testsuite.TestSuite import generate_wsgi

load_dotenv(find_dotenv())

DATABASES = {
    'default': {
        'driver': os.environ.get('DB_DRIVER'),
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_DATABASE'),
        'user': os.environ.get('DB_USERNAME'),
        'password': os.environ.get('DB_PASSWORD'),
        'prefix': ''
    }
}

DB = DatabaseManager(DATABASES)
Model.set_connection_resolver(DB)

class EntryTest(Model):
    __table__ = 'entry_test'
    __fillable__ = ['name']
    __timestamps__ = False

    def all(self):
        return {'test': 'test'}

class EntryTestResource(Resource, JsonSerialize, JWTAuthentication):
    model = EntryTest
    url = '/api/entrytest'
    scopes = ['user:read']
    data_wrap = False

REQUEST = Request(generate_wsgi())

class TestEncryptedAuthentication:

    def setup_method(self):
        self.app = App()
        self.request = REQUEST.load_app(self.app)

    def test_encrypted_token_returns_error_with_no_credentials(self):
        response = JWTGrantController().generate(self.request)
        assert response['error']
    
    def test_encrypted_token_returns_token_with_credentials(self):
        self.request.request_variables = {'username': 'test', 'password': 'secret', 'scopes': 'user:read user:show'}
        response = JWTGrantController().generate(self.request)
        assert response['token']
        token = response['token']

        self.request.request_variables = {'token': token}
        self.request.environ['REQUEST_METHOD'] = 'GET'
        self.request.path = '/api/entrytests'
        response = EntryTestResource().load_request(self.request).handle()
        assert response == '{"test": "test"}'

        ## Test valid token returns response
        self.request.request_variables = {'token': token}
        self.request.environ['REQUEST_METHOD'] = 'GET'
        self.request.path = '/api/entrytests'
        response = EntryTestResource().load_request(self.request).handle()
        assert response == '{"test": "test"}'

        ## Test returns error with invalid token
        token = 'invalid.token.given'
        self.request.request_variables = {'token': token}
        self.request.environ['REQUEST_METHOD'] = 'GET'
        self.request.path = '/api/entrytests'
        response = EntryTestResource().load_request(self.request).handle()
        assert response.startswith('{"error":')
