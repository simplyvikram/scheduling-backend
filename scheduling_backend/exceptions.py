
import json

class UserException(Exception):

    def __init__(self, message, code=400):
        """
        We create an exception with data and message attributes as that is
        what flask-restful uses to propgate the error message in json response
        inside Api.handle_error(e)
        """
        self.code = code
        self.message = message
        self.data = json.dumps({"error": message})


def generate_REST_exception(e):
    if type(e) == UserException:
        return e
    else:
        # Some exception raised somewhere down the request path, return some
        # readable message
        # todo log this appropriately
        return UserException(str(e), 400)

