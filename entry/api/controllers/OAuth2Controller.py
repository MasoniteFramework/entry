from masonite.auth import Sign
from masonite.facades import Auth
from masonite.view import View
import pendulum
import json
from entry.api.models.Scope import Scope
from entry.api.models.Application import Application
from entry.api.models.Token import Token
from urllib.parse import urlencode
import uuid
import pendulum

from masonite.request import Request

class OAuth2Controller:

    __application__ = Application
    __token__ = Token
    __scope__ = Scope

    def __init__(self):
        pass
    
    def show(self, request: Request, view: View):
        client_id = request.input('client_id')
        redirect_uri = request.input('redirect_uri')
        if request.has('state'):
            state = request.input('state')
        else:
            state = ''

        # Find Application
        client = self.__application__.where('client_id', client_id).first()

        scopes = []
        if request.has('scope'):
            for scope in request.input('scope').split(' '):
                db_scope = self.__scope__.where('name', scope).first()
                if db_scope:
                    scopes.append(db_scope)
        
        print(client)
        
        return view.render('/entry/views/oauth2', {'scopes': scopes, 'app_name': client.name, 'app_description': client.description, 'redirect_uri': redirect_uri, 'state': state})
    
    def send(self, request: Request):
        scopes = []
        for value in request.all():
            if value.startswith('scope-'):
                scopes.append(value.replace('scope-', ''))

        code = uuid.uuid4().hex

        Token.create(
            user_id = 1,
            token = "{}".format(uuid.uuid4().hex),
            code = code,
            refresh_token = "{}{}".format(uuid.uuid4().hex, uuid.uuid4().hex),
            expires_at = pendulum.now().add(days=1).to_datetime_string(),
            scopes = ' '.join(scopes)
        )


        return request.redirect('{0}?code={1}'.format(request.input('redirect_uri'), code))

    def refresh(self):
        pass
    
    def authorize(self, request: Request):
        client_id = request.input('client_id')
        client_secret = request.input('client_secret')
        grant_type = request.input('grant_type')
        code = request.input('code')
        redirect_uri = request.input('redirect_uri')

        client = Application.where('client_id', client_id).first()

        if client.client_secret != client_secret:
            return {'error': 'client secret does not match'}
        
        token = Token.where('code', code).first()

        if not token:
            return {'error': 'Token does not exist'}
        
        if token.code != request.input('code'):
            return {'error': 'Invalid token'}

        return {
            "access_token": token.token,
            "token_type": "Bearer",
            "expires_in": 604800,
            "refresh_token": token.refresh_token,
            "scope": token.scopes
        }

    def token(self):
        """ Exchange the authorization code an access token """
        pass

    def revoke(self):
        pass
