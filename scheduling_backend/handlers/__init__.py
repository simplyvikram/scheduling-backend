
from functools import wraps

from scheduling_backend.utils import JsonUtils


class MessageDict(object):
    request_not_in_json = {"Error": "Request is not in valid json format"}


def object_id_handler(func):
    """
    We use this before get/post/put/patch as we want the object ids in string
    format to be converted to the respective ObjectIds before we process
    them in the get/post/put/patch methods of the respective handlers
    """

    @wraps(func)
    def wrapper(inst, *args, **kwargs):
        """
        We extract inst(could have even used args[0]) as we want to
        set the data field of the resource object calling the func
        """

        if inst.data is not None:
            inst.data = JsonUtils.change_str_ids_to_object_id(inst.data)

        resp = func(inst, *args, **kwargs)

        resp = JsonUtils.change_obj_ids_to_str_ids(resp)
        return resp

    return wrapper


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