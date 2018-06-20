''' Database Settings '''

import os
import json

from dotenv import find_dotenv, load_dotenv
from orator import DatabaseManager, Model
from entry.api.Resource import Resource
from entry.api.JsonSerialize import JsonSerialize
from entry.api.TokenAuthentication import TokenAuthentication
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

class EntryTestResource(Resource, JsonSerialize, TokenAuthentication):
    model = EntryTest
    url = '/api/entrytest'
    data_wrap = False

REQUEST = Request(generate_wsgi())

class TestAuthentication:

    def setup_method(self):
        self.app = App()
        self.request = REQUEST.load_app(self.app)
        self.resource = EntryTestResource() \
            .load_request(self.request)
        # Insert a record
        EntryTest.create(name = 'Test')

    def test_authentication_returns_token_not_found(self):
        self.request.path = '/api/entrytests'
        response = json.loads(self.resource.load_request(self.request).handle())
        assert response['error']
    
    def test_authentication_throws_wrong_token(self):
        self.request.path = '/api/entrytests'
        self.request.request_variables = {'name': 'jim'}
        response = json.loads(self.resource.load_request(self.request).handle())
        assert response['error']
    
    def test_passes_with_correct_token(self):
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables = {'name': 'jim', 'token': '1234'}
        response = json.loads(self.resource.load_request(self.request).handle())
        assert response['token']
    
    
    def test_passes_with_correct_header_with_token(self):
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.header('AUTHORIZATION', '1234', http_prefix=False)
        response = json.loads(self.resource.load_request(self.request).handle())
        assert response['token']
    
