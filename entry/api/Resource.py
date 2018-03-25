import json
from entry.api.exceptions import (
    ApiNotAuthenticated,
    NoApiTokenFound,
    PermissionScopeDenied,
    RateLimitReached,
)

# TODO: 
#    - create tokens
#        - need to make a helper class which will create tokens
class Resource:

    exclude = []
    url = None
    model = None
    methods = ['create', 'read', 'update', 'delete']

    def __init__(self):
        self.model.__hidden__ = self.exclude
        if not self.url:
            self.url = '/api/{0}'.format(self.model().__class__.__name__.lower())
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
        if hasattr(self, 'limit'):
            try:
                self.limit()
            except RateLimitReached:
                return json.dumps({'error': 'Rate limit of {0} calls every {1} {2} reached'.format(self.rate_limit[0], self.rate_limit[1], self.rate_limit[2])})

        return self.serialize()
    
    def load_request(self, request):
        self.request = request
        return self

    def load_container(self, container):
        self.container = container
        return self