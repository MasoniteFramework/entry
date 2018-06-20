''' Database Settings '''

import os
import json

from dotenv import find_dotenv, load_dotenv
from orator import DatabaseManager, Model
from entry.api.Resource import Resource
from entry.api.JsonSerialize import JsonSerialize
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

class EntryTestResource(Resource, JsonSerialize):
    model = EntryTest
    url = '/api/entrytest'
    data_wrap = False


REQUEST = Request(generate_wsgi())


class TestResource():


    def setup_method(self):
        self.app = App()
        self.request = REQUEST.load_app(self.app)
        self.resource = EntryTestResource() \
            .load_request(self.request)
        # Insert a record
        EntryTest.create(name = 'Test')
    

    def test_insert(self):
        EntryTest.create(name='Test')
        assert EntryTest.all().count() > 0


    def test_resource_returns_json(self):
        self.request.path = '/api/entrytests'
        response = json.loads(self.resource.load_request(self.request).handle())[0]
        assert response['name'] == 'Test'

    
    def test_resource_returns_reads_all_and_single(self):
        # creates a resource
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        # self.request.request_variables = {'name': 'BOB'}
        self.request.request_variables = {'name': 'BOB'}

        response = json.loads(
            self.resource.load_request(self.request).handle())
            
        assert response['name'] == 'BOB'

        # read a single resource
        self.request.path = '/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'GET'
        response = json.loads(
            self.resource.load_request(self.request).handle())
        assert response['name'] == 'BOB'


    def test_resource_creates_on_post(self):
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables = {'name': 'BOB'}

        response = json.loads(self.resource.load_request(self.request).handle())
        assert response['name'] == 'BOB'


    def test_resource_updates_on_put(self):
        # Create a record
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables = {'name': 'BOB'}
        response = json.loads(
            self.resource.load_request(self.request).handle())
        
        # Update the record
        self.request.path = '/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'PUT'
        self.request.request_variables = {'name': 'BOB'}
        response = json.loads(
            self.resource.load_request(self.request).handle())
        
        assert response['name'] == 'BOB'


    def test_resource_deletes_on_delete(self):
        # Create a record
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables = {'name': 'BOB'}
        response = json.loads(
            self.resource.load_request(self.request).handle())
        
        # DELETE the record
        self.request.path = '/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'DELETE'
        response = json.loads(
            self.resource.load_request(self.request).handle())

        assert response['name'] == 'BOB'

    def test_read_only_fields(self):
        # Create a record
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables = {'name': 'BOB'}
        response = json.loads(
            self.resource.load_request(self.request).handle())

        # set the read only field
        self.resource.read_only_fields = ['name']

        # Update the record
        self.request.path = '/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'PUT'
        self.request.request_variables = {'name': 'CHANGE'}

        response = json.loads(
            self.resource.load_request(self.request).handle())
        assert response['name'] == 'BOB'

    def test_url_prefix(self):
        # Create a record
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables = {'name': 'BOB'}
        response = json.loads(
            self.resource.load_request(self.request).handle())

        # set the url_prefix field
        self.resource = EntryTestResource
        self.resource.url_prefix = '/v1'
        self.resource = self.resource()

        # read a single resource
        self.request.path = '/v1/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'GET'
        response = json.loads(
            self.resource.load_request(self.request).handle())
        assert response['name'] == 'BOB'

        # read all resources
        self.request.path = '/v1/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'GET'
        response = json.loads(
            self.resource.load_request(self.request).handle())
        assert len(response) == 2

    def test_data_wrap(self):
        # Create a record
        self.request.path = '/v1/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables = {'name': 'TEST'}
        response = json.loads(
            self.resource.load_request(self.request).handle())
        
        # set the read only field
        self.resource.data_wrap = True

        # read a single resource
        self.request.path = '/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'GET'
        response = json.loads(
            self.resource.load_request(self.request).handle())
        assert response['data']['name'] == 'TEST'

    def teardown_method(self):
        EntryTest.where('id', '<', 999999999999).delete()
