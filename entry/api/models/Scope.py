''' A OAuthToken Database Model '''
from config.database import Model

class Scope(Model):
    __table__ = 'oauth2_scopes'

    __fillable__ = ['name', 'description']