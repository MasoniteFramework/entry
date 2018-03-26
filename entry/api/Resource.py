import json
import bcrypt
import re
from entry.api.exceptions import (
    ApiNotAuthenticated,
    NoApiTokenFound,
    PermissionScopeDenied,
    RateLimitReached,
)

class Resource:

    exclude = []
    exclude_relationship_fields = []
    methods = ['create', 'read', 'update', 'delete']
    model = None
    relationships = None
    request = None
    url = None
    url_prefix = ''
    read_only_fields = []

    def __init__(self):
        self.model.__hidden__ = self.exclude
        if not self.url:
            self.url = '/api/{0}'.format(self.model().__class__.__name__.lower())
        
        if self.url_prefix:
            self.url = '{0}{1}'.format(self.url_prefix, self.url)

        self.container = None

    def handle(self):

        # Run authentication if one exists
        if hasattr(self, 'authenticate'):
            try:
                self.authenticate()
            except ApiNotAuthenticated:
                return json.dumps({'error': 'Invalid authentication token'})
            except NoApiTokenFound:
                return json.dumps({'error': 'Authentication token not found'})
            except PermissionScopeDenied:
                return json.dumps({'error': 'Incorrect permission scope'})

        # Run rate limiting if one exists
        if hasattr(self, 'limit'):
            try:
                self.limit()
            except RateLimitReached:
                return json.dumps({'error': 'Rate limit of {0} calls every {1} {2} reached'.format(self.rate_limit[0], self.rate_limit[1], self.rate_limit[2])})

        for item in list(self.model().__dict__):
            if item.startswith('_'):
                self.model().__dict__.pop(item)

        try:
            if self.request.environ['REQUEST_METHOD'] == 'POST' and 'create' in self.methods:
                return self.serialize(self.create())

            if self.request.environ['REQUEST_METHOD'] == 'GET' and 'read' in self.methods:
                return self.serialize(self.read())

            if self.request.environ['REQUEST_METHOD'] == 'PUT' and 'update' in self.methods:

                return self.serialize(self.update())

            if self.request.environ['REQUEST_METHOD'] == 'DELETE' and 'delete' in self.methods:
                return self.serialize(self.delete())
        except Exception as e:
            return self.serialize({'error': str(e)})

        return self.serialize(
            {
                'Error': 'Invalid URI: {0} {1}. This route does not exist for this endpoint.'.format(
                    self.request.environ['REQUEST_METHOD'], self.request.path)
            }
        )
    
    def load_request(self, request):
        self.request = request
        return self

    def load_container(self, container):
        self.container = container
        return self

    def create(self):
        if '{0}s'.format(self.url) == self.request.path:
            # if POST /api/users
            proxy = self.model()
            for field in self.request.all():
                # If the field is a password, hash it
                if field == 'password':
                    password = bcrypt.hashpw(
                        bytes(self.request.input('password'),
                              'utf-8'), bcrypt.gensalt()
                    )
                    setattr(proxy, field, password)
                else:
                    setattr(proxy, field, self.request.input(field))
            proxy.save()

            return proxy

    def read(self):
        matchregex = re.compile(r'^[\/\w+]+\/(\d+)')
        match_url = matchregex.match(self.request.path)

        # Get the plural of the url
        if '{0}s'.format(self.url) == self.request.path:
            # if GET /api/users
            models = self.model().all()
            if self.relationships:
                for model in models:
                    self._get_relationships(model)

            return models
        elif match_url:
            record = self.model().find(match_url.group(1))
            if record:
                if self.relationships:
                    self._get_relationships(record)
                return record
            else:
                return {'Error': 'Record Not Found'}

        return {'Error': 'Invalid URI: {0}'.format(self.request.path)}

    def update(self):
        # if PUT /api/user/1
        matchregex = re.compile(r"^\/\w+\/\w+\/(\d+)")
        match_url = matchregex.match(self.request.path)

        proxy = self.model.find(match_url.group(1))
        if not proxy:
            return {'Error': 'Record Not Found'}

        for field in self.request.all():
            if field not in self.read_only_fields:
                setattr(proxy, field, self.request.input(field))
        proxy.save()
        proxy = self.model.find(match_url.group(1))
        return proxy

    def delete(self):
        # if DELETE /api/user/1
        matchregex = re.compile(r"^\/\w+\/\w+\/(\d+)")
        match_url = matchregex.match(self.request.path)

        get = self.model.find(match_url.group(1))
        if get:
            get.delete()
            return get
        else:
            return {'Error': 'Record Not Found'}

    def _get_relationships(self, model):
        # Get relationships
        for relationship in self.relationships:
            if hasattr(model, relationship):
                attr = getattr(model, relationship)
                if attr and relationship in self.exclude_relationship_fields:
                    attr.__hidden__ = self.exclude_relationship_fields[relationship]
