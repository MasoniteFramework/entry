''' A Module Description '''
from app.User import User
from masonite.facades.Auth import Auth


class PasswordGrant:
    ''' Class Docstring Description '''

    def generate(self, Request):
        user = Auth(Request).login(Request.input(
            'username'), Request.input('password'))

        if user:
            return {'token': user.create_token()}
        else:
            return {'Error': 'Incorrect username or password'}
