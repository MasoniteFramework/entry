''' Authentication Settings '''

'''
|--------------------------------------------------------------------------
| Authentication Model
|--------------------------------------------------------------------------
|
| Put the model here that will be used to authenticate users to your site.
| Currently the model must contain a password field. In the model should
| be an auth_column = 'column' in the Meta class. This column will be
| used to verify credentials in the Auth facade or any other auth
| classes. The auth_column will be used to change auth things
| like 'email' to 'user' to easily switch which column will
| be authenticated.
|
| @see masonite.facades.Auth
|
'''

class MockAuth:

    __auth__ = 'email'
    password = '$2b$12$zWTCn.SgvljX74yv.krMZeZOkx73rh.m5mksgq3QQuI/xjize7.L2'

    def where(self, column, column_to):
        # print('self': self)
        return self
    
    def first(self):
        return self
    
    def save(self):
        return self


AUTH = {
    'driver': 'cookie',
    'model': MockAuth(),
}
