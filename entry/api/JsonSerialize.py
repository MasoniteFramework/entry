import json
import re
import bcrypt

class JsonSerialize:
    model = None
    request = None
    url = None
    relationships = None
    exclude_relationship_fields = []

    def serialize(self):
        for item in list(self.model().__dict__):
            if item.startswith('_'):
                self.model().__dict__.pop(item)
        
        try:
            if self.request.environ['REQUEST_METHOD'] == 'POST' and 'create' in self.methods:
                return self.create()

            if self.request.environ['REQUEST_METHOD'] == 'GET' and 'read' in self.methods:
                return self.read()

            if self.request.environ['REQUEST_METHOD'] == 'PUT' and 'update' in self.methods:
                return self.update()
            
            if self.request.environ['REQUEST_METHOD'] == 'DELETE' and 'delete' in self.methods:
                return self.delete()
        except Exception as e:
            return json.dumps(
                {
                    'error': str(e)
                }
            )

        return json.dumps(
            {
                'Error': 'Invalid URI: {0} {1}. This route does not exist for this endpoint.'.format(
                self.request.environ['REQUEST_METHOD'], self.request.path)
            }
        )

    def create(self):
        if '{0}s'.format(self.url) == self.request.path:
            # if POST /api/users
            proxy = self.model()
            for field in self.request.all():

                # If the field is a password, hash it
                if field == 'password':
                    password = bcrypt.hashpw(
                        bytes(self.request.input('password'), 'utf-8'), bcrypt.gensalt()
                    )
                    setattr(proxy, field, password)
                else:
                    setattr(proxy, field, self.request.input(field))
            proxy.save()
            return proxy.to_json()

    def _get_relationships(self, model):
        # Get relationships
        for relationship in self.relationships:
            if hasattr(model, relationship):
                attr = getattr(model, relationship)
                if attr and relationship in self.exclude_relationship_fields:
                    attr.__hidden__ = self.exclude_relationship_fields[relationship]

    def read(self):
        matchregex = re.compile(r"^\/\w+\/\w+\/(\d+)")
        match_url = matchregex.match(self.request.path)

        # Get the plural of the url
        if '{0}s'.format(self.url) == self.request.path:
            # if GET /api/users
            models = self.model().all()
            if self.relationships:
                for model in models:
                    self._get_relationships(model)
                        
            return models.to_json()
        elif match_url:
            # if GET /api/user/1
            record = self.model().find(match_url.group(1))
            if record:
                if self.relationships:
                    self._get_relationships(record)
                return record.to_json()
            else:
                return json.dumps({'Error': 'Record Not Found'})

        return json.dumps({'Error': 'Invalid URI: {0}. Did you mean {0}s?'.format(self.url)})

    def update(self):
        # if PUT /api/user/1
        matchregex = re.compile(r"^\/\w+\/\w+\/(\d+)")
        match_url = matchregex.match(self.request.path)

        proxy = self.model.find(match_url.group(1))
        if not proxy:
            return json.dumps({'Error': 'Record Not Found'})

        for field in self.request.all():
            setattr(proxy, field, self.request.input(field))
        proxy.save()
        proxy = self.model.find(match_url.group(1))
        return proxy.to_json()

    def delete(self):
        # if DELETE /api/user/1
        matchregex = re.compile(r"^\/\w+\/\w+\/(\d+)")
        match_url = matchregex.match(self.request.path)

        get = self.model.find(match_url.group(1))
        if get:
            get.delete()
            return get.to_json()
        else:
            return json.dumps({'Error': 'Record Not Found'})
