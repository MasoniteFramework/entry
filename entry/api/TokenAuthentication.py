from entry.api.exceptions import ApiNotAuthenticated, NoApiTokenFound
from urllib.parse import parse_qs
from masonite.routes import Post


class TokenAuthentication:

    authentication_model = None
    routes = [
        Post().module('app.http.controllers.Api').route('/oauth/token', 'OAuthPasswordGrant@generate'),
    ]
    authenticated_methods = ['create', 'read', 'update', 'delete']

    def authenticate(self):
        if not self.authentication_model:
            self.authentication_model = self.obj
        
        if not self.request.has('token'):
            raise NoApiTokenFound

        if not self.authentication_model.where('token', self.request.input('token')).count():
            raise ApiNotAuthenticated
        
        # Delete the token input
        if self.request.is_not_get_request():
            build_new_inputs = {}
            for i in self.request.params:
                build_new_inputs[i] = self.request.params[i]
            
            build_new_inputs.pop('token')
            self.request.params = build_new_inputs
    
        
    def tokens_from_model(self, model):
        self.authentication_model = model
        return self
