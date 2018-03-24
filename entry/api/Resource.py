import json
from entry.api.exceptions import ApiNotAuthenticated, NoApiTokenFound, PermissionScopeDenied

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
        return self.serialize()
    
    def load_request(self, request):
        self.request = request
        return self
