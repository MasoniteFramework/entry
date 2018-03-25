''' Database Settings '''

import os
import json

from dotenv import find_dotenv, load_dotenv
from orator import DatabaseManager, Model
from entry.api.Resource import Resource
from entry.api.JsonSerialize import JsonSerialize
from masonite.app import App
from masonite.request import Request

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


WSGI_REQUEST = {
    'wsgi.version': (1, 0),
    'wsgi.multithread': False,
    'wsgi.multiprocess': True,
    'wsgi.run_once': False,
    'SERVER_SOFTWARE': 'gunicorn/19.7.1',
    'REQUEST_METHOD': 'GET',
    'QUERY_STRING': '',
    'RAW_URI': '/',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'HTTP_HOST': '127.0.0.1:8000',
    'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'HTTP_UPGRADE_INSECURE_REQUESTS': '1',
    'HTTP_COOKIE': 'setcookie=value',
    'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7',
    'HTTP_ACCEPT_LANGUAGE': 'en-us',
    'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
    'HTTP_CONNECTION': 'keep-alive',
    'wsgi.url_scheme': 'http',
    'REMOTE_ADDR': '127.0.0.1',
    'REMOTE_PORT': '62241',
    'SERVER_NAME': '127.0.0.1',
    'SERVER_PORT': '8000',
    'PATH_INFO': '/',
    'SCRIPT_NAME': ''
}

REQUEST = Request(WSGI_REQUEST)


class TestResource():


    def setup_method(self):
        self.request = REQUEST
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
        self.request.params = 'name=BOB'

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
        self.request.params = 'name=BOB'

        response = json.loads(self.resource.load_request(self.request).handle())
        assert response['name'] == 'BOB'


    def test_resource_updates_on_put(self):

        # Create a record
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.params = 'name=BOB'
        response = json.loads(
            self.resource.load_request(self.request).handle())
        
        # Update the record
        self.request.path = '/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'PUT'
        self.request.params = 'name=BOB'
        response = json.loads(
            self.resource.load_request(self.request).handle())
        
        assert response['name'] == 'BOB'


    def test_resource_deletes_on_delete(self):
        # Create a record
        self.request.path = '/api/entrytests'
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.params = 'name=BOB'
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
        self.request.params = 'name=BOB'
        response = json.loads(
            self.resource.load_request(self.request).handle())

        # set the read only field
        self.resource.read_only_fields = ['name']

        # Update the record
        self.request.path = '/api/entrytests/{0}'.format(response['id'])
        self.request.environ['REQUEST_METHOD'] = 'PUT'
        self.request.params = 'name=CHANGE'

        response = json.loads(
            self.resource.load_request(self.request).handle())
        assert response['name'] == 'BOB'

    def teardown_method(self):
        EntryTest.where('id', '<', 999999999999).delete()
