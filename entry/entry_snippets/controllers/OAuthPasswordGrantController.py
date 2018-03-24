''' A Module Description '''
from app.User import User
from masonite.facades.Auth import Auth


class OAuthPasswordGrantController:
    ''' Class Docstring Description '''

    def generate(self, Request):
        user = Auth(Request).login(Request.input(
            'username'), Request.input('password'))

        if user:
            return {'token': user.create_token()}
        else:
            return {'error': 'Incorrect username or password'}

    def revoke(self, Request):
        user = Auth(Request).login(Request.input(
            'username'), Request.input('password'))

        if user:
            if user.revoke_token():
                return {'success': 'token revoked'}
            else:
                return {'error': 'Could not revoke token'}
        else:
            return {'error': 'Incorrect username or password'}