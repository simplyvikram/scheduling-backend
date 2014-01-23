
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

        print "Intercepting flask exception and generating a restful one-----",\
            str(e)

        return e
    else:
        # Some exception raised somewhere down the request path, return some
        # readable message
        # todo log this appropriately

        print "Caught Flask exception------", str(e)
        return UserException(str(e), 400)

