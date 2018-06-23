''' A Module Description '''
from masonite.facades.Auth import Auth
from masonite.request import Request
from cryptography.fernet import Fernet
from masonite.auth import Sign
import pendulum
import json
from entry.helpers import expiration_time


class EncryptedGrantController:
    ''' Class Docstring Description '''

    __auth__ = Auth

    def generate(self, request: Request):
        # generate a secret key and sign it based on your server secret key
        if not request.has('username') or not request.has('password'):
            return {'error': 'This API call requires a username and password in the payload.'}

        user = self.__auth__(request).login(request.input(
            'username'), request.input('password'))
        
        if user:
            # user is authenticated
            if request.has('scope'):
                scopes = request.input('scopes')
            else:
                scopes = ''

            # generate a new key and signed with the secret key
            payload = {
                'issued': str(pendulum.now()),
                'expires_at': str(pendulum.now().add(days=1)),
                'scope': scopes
            }

            return {'token': Sign().sign(json.dumps(payload))}

    def refresh(self, request: Request):
        if not request.input('token'):
            return {'error': 'No Token Found'}

        try:
            token = Sign().unsign(request.input('token'))
        except DecodeError:
            return {'error': 'Could not decode token'}


        # generate a new key and signed with the secret key
        payload = {
            'issued': str(pendulum.now()),
            'expires': str(pendulum.now().add(days=1))
        }

        return {'token': Sign().sign(json.dumps(payload))}