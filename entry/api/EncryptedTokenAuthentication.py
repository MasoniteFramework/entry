from entry.api.exceptions import ApiNotAuthenticated, NoApiTokenFound, PermissionScopeDenied
from urllib.parse import parse_qs
from masonite.routes import Post, Delete
from entry.api.models.OAuthToken import OAuthToken
from masonite.auth import Sign
from entry.helpers import expiration_time
import pendulum
import json


class EncryptedTokenAuthentication:
    scopes = ['*']
    expires_in = '5 minutes'

    def authenticate(self):
        # Find which input has the authorization token:

        token = self.get_token()

        unsign_token = json.loads(Sign().unsign(token))

        if not self.check_time(unsign_token):
            raise ApiNotAuthenticated

        # Check correct scopes:
        scopes = unsign_token['scopes'].split(' ')

        if '*' not in self.scopes:
            if not set(self.scopes).issubset(scopes):
                raise PermissionScopeDenied

        # Delete the token input
        if self.request.has('token') and self.request.is_not_get_request():
            build_new_inputs = {}
            for i in self.request.request_variables:
                build_new_inputs[i] = self.request.request_variables[i]
            
            build_new_inputs.pop('token')
            self.request.request_variables = build_new_inputs

    def get_token(self):
        if self.request.has('token'):
            return self.request.input('token')
        elif self.request.header('AUTHORIZATION'):
            return self.request.header('AUTHORIZATION').replace('Bearer ', '')
        
        # Check if Authentication token exists
        if not self.request.header('AUTHORIZATION') and not self.request.has('token'):
            raise NoApiTokenFound
  
    def check_time(self, unsign_token):
        issued_time = unsign_token['issued']
        minutes_ago = expiration_time(self.expires_in)

        expiration = self.expires_in.split(' ')
        expiration_amount = int(expiration[0])

        time_parse = pendulum.parse(issued_time).diff(pendulum.parse(minutes_ago))

        if expiration[1] in ('minute', 'minutes'):
            if time_parse.in_minutes() < expiration_amount \
                and not time_parse.in_seconds() <= 0:
                
                return True
            
            return False
        
        if expiration[1] in ('hour', 'hours'):
            if time_parse.in_hours() < expiration_amount \
                and not time_parse.in_minutes() <= 0 \
                and not time_parse.in_seconds() <= 0:
                return True
            
            return False
        
        return False
        

    

    @staticmethod
    def routes():
        try:
            return [
                Post().module('app.http.controllers.Entry.Api').route('/oauth/token', 'OAuthPasswordGrantController@generate'),
                Delete().module('app.http.controllers.Entry.Api').route('/oauth/token', 'OAuthPasswordGrantController@revoke'),
            ]
        except ImportError as e:
            print("\033[93mWarning: could not find app.http.controllers.Entry.Api - Error {0}".format(e))
        
        return []
