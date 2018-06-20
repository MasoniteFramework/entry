''' A Module Description '''
from masonite.facades.Auth import Auth
import pendulum
import json
from entry.helpers import expiration_time
import jwt
from config import application


class JWTGrantController:
    ''' Class Docstring Description '''

    def generate(self, Request):
        if not Request.has('username') or not Request.has('password'):
            return {'error': 'This API call requires a username and password in the payload.'}

        user = Auth(Request).login(
            Request.input('username'), 
            Request.input('password')
        )
        
        if Request.has('scopes'):
            scopes = Request.input('scopes')
        else:
            scopes = ''

        if user:
            # get the current time
            current_time = str(pendulum.now())

            payload = {
                'issued': current_time,
                'scopes': scopes,
                'expires': str(pendulum.now().add(minutes=5))
            }

            encoded = jwt.encode(payload, application.KEY, algorithm='HS256').decode('UTF-8')
            return {'token': encoded}
        else:
            return {'error': 'Incorrect username or password'}
