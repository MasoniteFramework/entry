import json



class JsonSerialize:

    def serialize(self, data):
        if isinstance(data, dict):
            return json.dumps(data)
        else:
            return data.to_json()
        

