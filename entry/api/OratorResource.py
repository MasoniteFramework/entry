import re

class OratorResource:

    def __init__(self, obj):
        self.obj = obj

        self.method_type = 'POST'
        self.continueroute = True
        self.url = False
        self.exclude_list = []
        self.output = False
        self.model_obj = None

    def load_request(self, request):
        self.request = request

    def create(self):
        """
            POST api/User
        """

        pass

    def read(self):
        """
            GET api/User
            GET api/User/1
        """
        
        """ Fetch the API from the model """
        # regex for /api/users
        matchregex = re.compile(r"^\/\w+\/\w")

        if self.url == self.request.path and self.request.method == 'GET':
            # if GET /api/user

            model = self.model_obj
            model.__hidden__ = self.exclude_list

            query = model.all()

            self.output = query.to_json()

    def update(self):
        """
            PUT / PATCH api/User/1
        """
        pass 

    def delete(self):
        """
            DELETE api/User/1
        """
        pass
