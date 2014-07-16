
from functools import wraps

from flask.ext.restful.reqparse import RequestParser
from flask import request

from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.models import Employee, Equipment, User
from scheduling_backend.utils import JsonUtils
from scheduling_backend.user_operations import UserOperations

class MessageDict(object):
    request_not_in_json = {"Error": "Request is not in valid json format"}


class Params(object):

    INCLUDE_JOBSHIFTS = "includejobshifts"
    INCLUDE_EMPLOYEESHIFTS = "includeemployeeshifts"
    ACTIVE = "active"
    DEFAULT_ROLE = "default_role"
    SHIFT_ROLE = "shift_role"
    JOB_ID = "job_id"
    FROM_DATE = "from_date"
    TO_DATE = "to_date"
    INCLUDE_SATURDAY = "include_saturday"
    INCLUDE_SUNDAY = "include_sunday"


def authentication_handler(func):

    @wraps(func)
    def wrapper(inst, *args, **kwargs):

        header_parser = RequestParser()
        header_parser.add_argument(User.Fields.USERNAME,
                                   type=str,
                                   required=True,
                                   location='headers',
                                   help='username needs to be present in header')

        header_parser.add_argument(User.Fields.PASSWORDHASH,
                                   type=str,
                                   required=True,
                                   location='headers',
                                   help='password hash needs to be present in header')

        headers = header_parser.parse_args()

        request._username = headers[User.Fields.USERNAME]
        request._passwordhash = headers[User.Fields.PASSWORDHASH]

        user = UserOperations.find_user_with_passwordhash(
            request._username,
            request._passwordhash
        )


        if not user:
            return "Cannot authenticte user", 401
            # raise UserException("Could not authenticate user")

        return func(inst, *args, **kwargs)

    return wrapper


# from flask import request, redirect, current_app
# def ssl_required(fn):
#     @wraps(fn)
#     def decorated_view(*args, **kwargs):
#         if current_app.config.get("SSL"):
#             if request.is_secure:
#                 return fn(*args, **kwargs)
#             else:
#                 return redirect(request.url.replace("http://", "https://"))
#
#         return fn(*args, **kwargs)
#
#     return decorated_view


def marshaling_handler(func):
    """
    Decorator for get/post/put/patch as we want the object ids in string
    format to be converted to the ObjectId's before we process
    them in the get/post/put/patch methods of the respective handlers.
    It also converts ObjectId's inside request handler's response data to
    string in order to be sent as valid json
    """

    @wraps(func)
    def wrapper(inst, *args, **kwargs):
        """
        We extract inst(could have even used args[0]) as we want to
        set the data field of the resource object calling the func
        """
        if inst.data:
            inst.data = JsonUtils.change_all_str_objectids_to_objectids(
                inst.data
            )
            inst.data = \
                JsonUtils.change_all_date_time_to_include_leading_zeros(
                    inst.data
                )

        json_data = func(inst, *args, **kwargs)
        json_data = JsonUtils.change_all_objectids_to_str(json_data)

        cors_headers = {
            'Access-Control-Allow-Origin': '*'
        }

        return json_data, 200, cors_headers

    return wrapper


def delete_handler(func):
    """
    Decorator for REST delete operation, adds CORS support
    """

    cors_headers = {
        'Access-Control-Allow-Origin': '*'
    }

    @wraps(func)
    def wrapper(inst, *args, **kwargs):

        resp_data, status = func(inst, *args, **kwargs)

        return resp_data, status, cors_headers

    return wrapper


# todo fix this soon
# todo merge it with delete_handler() maybe??
# todo bad name, we actually return data here
def no_data_handler(func):
    cors_headers = {
        'Access-Control-Allow-Origin': '*'
    }

    @wraps(func)
    def wrapper(inst, *args, **kwargs):

        resp_data, status = func(inst, *args, **kwargs)

        return resp_data, status, cors_headers

    return wrapper



class EmployeeRoleHandler(BaseHandler):

    def __init__(self):
        super(EmployeeRoleHandler, self).__init__(None)

    def get(self):
        return Employee.allowed_roles()

class EquipmentTypeHandler(BaseHandler):

    def __init__(self):
        super(EquipmentTypeHandler, self).__init__(None)

    def get(self):
        return Equipment.allowed_types()