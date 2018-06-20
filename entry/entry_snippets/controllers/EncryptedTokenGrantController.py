''' A Module Description '''
from masonite.facades.Auth import Auth
from cryptography.fernet import Fernet
from masonite.auth import Sign
import pendulum
import json
from entry.helpers import expiration_time


class EncryptedTokenGrantController:
    ''' Class Docstring Description '''

    def generate(self, Request):
        if not Request.has('username') or not Request.has('password'):
            return {'error': 'This API call requires a username and password in the payload.'}

        user = Auth(Request).login(Request.input(
            'username'), Request.input('password'))
        
        if Request.has('scopes'):
            scopes = Request.input('scopes')
        else:
            scopes = ''

        if user:
            # create a random string
            token = Fernet.generate_key().decode('UTF-8')

            # get the current time
            current_time = str(pendulum.now())

            # create a string like: random-string:time
            # key = '{}--{}'.format(key, current_time)
            key = {
                'token': token,
                'issued': current_time,
                'scopes': scopes
            }
            sign = Sign().sign(json.dumps(key))
            return {'token': sign}
        else:
            return {'error': 'Incorrect username or password'}

    def revoke(self, Request):
        if not Request.has('token'):
            return {'error': 'Token not received'}

        get_token = OAuthToken.where('token', Request.input('token')).first()
        if get_token:
            get_token.delete()
            return {'success': 'Token was revoked'}
        else:
            return {'error': 'Could not find token'}
