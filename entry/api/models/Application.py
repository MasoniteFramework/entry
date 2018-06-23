''' A OAuthToken Database Model '''
from config.database import Model

class Application(Model):
    __table__ = 'oauth2_apps'

    __fillable__ = ['name', 'description', 'client_id', 'client_secret']