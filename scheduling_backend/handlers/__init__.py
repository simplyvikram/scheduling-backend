
from functools import wraps

from flask.ext.restful import Resource

from scheduling_backend.utils import JsonUtils


class MessageDict(object):
    request_not_in_json = {"Error": "Request is not in valid json format"}


def common_handler(func):

    @exception_handler
    @object_id_handler
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def exception_handler(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
            return resp
        except Exception as e:
            print "The following error occurred: ", e
            return {"error": str(e)}

    return wrapper


def object_id_handler(func):
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
        if inst.error:
            return inst.error

        if inst.data:
            inst.data = JsonUtils.change_str_ids_to_object_id(inst.data)

        resp = func(inst, *args, **kwargs)

        resp = JsonUtils.change_obj_ids_to_str_ids(resp)
        return resp


    return wrapper


class RoleHandler(Resource):

    def get(self):
        from scheduling_backend.models import Employee
        return Employee.allowed_roles()

# from flask import current_app, request, Response
# from scheduling_backend import the_context
#
# with the_context:
#
#     @current_app.before_request
#     def before(*args, **kwargs):
#         data = request.get_json(force=False, silent=True)
#         if data:
#             print "XX Before request - type:%s data:%s" % (type(data), data)
#             # data = JsonUtils.change_str_ids_to_object_id(data)
#             data = {"employeebefore": "fooooo"}
#         else:
#             print "XX Before reqquest - data is none"
#
#
#     @current_app.after_request
#     def after(response):
#
#         if response.data:
#             print "XX After request - data", str(response.data)
#             response.data = {"employeeafter": "barrrrr"}
#         else:
#             print "XX After request - data is none"
#
#
#         return Response(response=response.data, content_type="application/json")
#         # return response