import uuid
from entry.api.models.OAuthToken import OAuthToken

class HasApiTokens:
    """
        Helper Class For API Authentication Models
    """

    def create_token(self, name='default', scopes=''):
        """ Create a new API token and save to model """

        generated_token = uuid.uuid4().hex

        user_by_token = OAuthToken.where('user_id', self.id).first()

        if user_by_token:
            # update the token
            user_by_token.token = generated_token
            user_by_token.scope = scopes
            user_by_token.save()
        else:
            OAuthToken.create(
                user_id = self.id,
                name = name,
                scope = scopes,
                token = generated_token
            )

        return generated_token
    
    def get_token(self):
        """ Get current API Token """
        return OAuthToken.where('user_id', self.id).first().token


    def has_token(self):
        """ Check if user has an API token """

        if OAuthToken.where('user_id', self.id).first():
            return True
        
        return False
    
    def has_scope(self, scope):
        get_token = OAuthToken.where('user_id', self.id).first()
        
        if get_token:
            scopes = get_token.scope.split(' ')
            if scope in scopes:
                return True
        return False

    def with_token(self, token):
        """ Set API token for the current user """
        self.token = token
        return self
    
    def revoke_token(self):
        get_token = OAuthToken.where('user_id', self.id).first()
        if get_token:
            return get_token.delete()
        
        return False
