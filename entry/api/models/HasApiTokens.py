import uuid

class HasApiTokens:
    """
        Helper Class For API Authentication Models
    """

    def create_token(self):
        """ Create a new API token and save to model """

        generated_token = uuid.uuid4().hex
        self.token = generated_token
        self.save()

        return generated_token
    
    def get_token(self):
        """ Get current API Token """

        return self.token

    def has_token(self):
        """ Check if user has an API token """

        if self.token is not None:
            return True
        
        return False

    def with_token(self, token):
        """ Set API token for the current user """

        self.token = token
        return self
