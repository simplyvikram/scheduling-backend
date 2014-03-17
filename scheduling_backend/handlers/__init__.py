
from functools import wraps


from scheduling_backend.utils import JsonUtils
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.models import Employee, Equipment

class MessageDict(object):
    request_not_in_json = {"Error": "Request is not in valid json format"}


class Params(object):

    INCLUDE_JOBSHIFTS = "includejobshifts"
    INCLUDE_EMPLOYEESHIFTS = "includeemployeeshifts"
    ACTIVE = "active"
    CURRENT_ROLE = "current_role"
    SHIFT_ROLE = "shift_role"
    JOB_ID = "job_id"
    FROM_DATE = "from_date"
    TO_DATE = "to_date"
    INCLUDE_SATURDAY = "include_saturday"
    INCLUDE_SUNDAY = "include_sunday"


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