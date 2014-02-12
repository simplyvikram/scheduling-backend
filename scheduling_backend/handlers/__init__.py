
from functools import wraps
from flask.ext.restful import Resource
from scheduling_backend.utils import JsonUtils

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

        resp = func(inst, *args, **kwargs)

        resp = JsonUtils.change_all_objectids_to_str(resp)
        return resp

    return wrapper


class RoleHandler(Resource):

    def get(self):
        from scheduling_backend.models import Employee
        return Employee.allowed_roles()