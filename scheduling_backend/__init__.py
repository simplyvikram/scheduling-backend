
import logging
import os
import sys
from bson.objectid import ObjectId
from bson.errors import InvalidId

from pymongo import MongoClient
from flask import abort, Flask, request
from flask.ext.restful import Api
from werkzeug.routing import BaseConverter

from exceptions import UserException, generate_REST_exception


app_name = 'scheduling_backend'

global the_context

class ApiBase(Api):
    """
    Flask restful intercepts all exceptions and returns a totally useless
    JSON error. Here we add handlers to make sure the messages for both the
    user and regular exceptions get handled properly
    """

    def __init__(self, app=None, prefix='',
                 default_mediatype='application/json', decorators=None,
                 catch_all_404s=False):

        super(ApiBase, self).__init__(app, prefix,
                                      default_mediatype, decorators,
                                      catch_all_404s)

        app.handle_exception = self.handle_exception
        app.handle_user_exception = self.handle_user_exception


    def handle_exception(self, e):

        e = generate_REST_exception(e)

        if request.path.startswith(self.prefix):
            return super(ApiBase, self).handle_error(e)

        if request.endpoint in self.endpoints:
            return super(ApiBase, self).handle_error(e)
        else:
            return Flask.handle_exception(self.app, e)


    def handle_user_exception(self, e):

        import traceback
        traceback.print_exc()

        e = generate_REST_exception(e)

        if request.path.startswith(self.prefix):
            return super(ApiBase, self).handle_error(e)

        if request.endpoint in self.endpoints:
            return super(ApiBase, self).handle_error(e)
        else:
            return Flask.handle_exception(self.app, e)


class BsonObjectIdConverter(BaseConverter):
    """
    This is used to convert ObjectId's present in urls in string format to
    ObjectId objects we need in the respective url handlers

    Based on
    http://flask.pocoo.org/snippets/106/
    https://github.com/dcrosta/flask-pymongo/blob/master/flask_pymongo/__init__.py
    """

    def to_python(self, value):
        try:
            return ObjectId(value)
        except (InvalidId, ValueError, TypeError) as e:
            print "Error while url routing -", repr(e)
            raise abort(400)

    def to_url(self, value):
        return str(value)


def create_app(name, config_object):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        appname: name of the Flask app to create
        object_name: the python path of the config object,
                     e.g. appname.settings.ProdConfig

        env: The name of the current environment, e.g. prod or dev
    """
    app = Flask(name)

    global the_context
    the_context = app.app_context()

    app.config.from_object(config_object)

    # we want the view to be accessible

    enable_logging(app)
    register_views(app)

    init_db(app)
    return app


def init_db(app):
    client = MongoClient(app.config['MONGODB_URI'])
    db = client[app.config['MONGODB_NAME']]
    app.db = db


def register_views(app):
    api = ApiBase(app)

    app.url_map.converters['ObjectId'] = BsonObjectIdConverter

    from handlers.job_handler import JobHandler
    from handlers.client_handler import ClientHandler
    from handlers.employee_handler import EmployeeHandler
    from handlers.jobshift_handler import JobShiftHandler
    from handlers.employeeshift_handler import (
        AddEmployeeShiftHandler,
        RemoveEmployeeShiftHandler,
        MoveEmployeeAcrossJobshifts,
        ModifyEmployeeShiftHandler
    )
    from handlers.date_handler import DateHandler
    from handlers.copy_jobshift_handler import (
        CopyJobshiftHandler,
        CopyAllJobshiftsHandler
    )
    from handlers import RoleHandler
    from handlers.reporting_handler import (
        HoursWorkedPerEmployeeHandler,
        HoursWorkedPerShiftRole
    )

    api.add_resource(ClientHandler, '/clients/<ObjectId:obj_id>',
                     endpoint="client")
    api.add_resource(ClientHandler, '/clients', endpoint="clients")


    api.add_resource(EmployeeHandler, '/employees/<ObjectId:obj_id>',
                     endpoint="employee")
    api.add_resource(EmployeeHandler, '/employees', endpoint="employees")


    # for jobs, include a parameter to include jobshifts, jobshifts_ids/jobshifts
    api.add_resource(JobHandler, '/jobs/<ObjectId:job_id>', endpoint="job")
    api.add_resource(JobHandler, '/jobs', endpoint="jobs")


    # only PATCH and GET supported
    # Jobshift creation/deletion is only done when jobs are created/deleted
    # PATCH would change a job shift
    api.add_resource(JobShiftHandler,
                     '/jobshifts/<ObjectId:jobshift_id>',
                     endpoint="jobshift")

    # params shift_role, if absent use employee's current role
    api.add_resource(AddEmployeeShiftHandler,
                     '/add'
                     '/employee/<ObjectId:employee_id>'
                     '/jobshift/<ObjectId:jobshift_id>',
                     endpoint="addemployeeshift")


    # add/employee/22/jobshift/400
    api.add_resource(RemoveEmployeeShiftHandler,
                     '/remove'
                     '/employee/<ObjectId:employee_id>'
                     '/jobshift/<ObjectId:jobshift_id>',
                     endpoint="removeemployeeshift")

    # params shift_role, if absent use employee's shift role
    api.add_resource(MoveEmployeeAcrossJobshifts,
                     '/move'
                     '/employee/<ObjectId:employee_id>'
                     '/fromjobshift/<ObjectId:from_jobshift_id>'
                     '/tojobshift/<ObjectId:to_jobshift_id>',
                     endpoint="moveemployeeshift")

    # add ability to modify role too
    api.add_resource(ModifyEmployeeShiftHandler,
                     '/modify'
                     '/jobshift/<ObjectId:jobshift_id>'
                     '/employee/<ObjectId:employee_id>',
                     endpoint="modifyemployeeshift")

    api.add_resource(DateHandler,
                     '/<string:collection_name>/date/<string:_date>',
                     endpoint="date_operations")

    # params - include_sunday, include_saturday
    api.add_resource(CopyJobshiftHandler,
                     '/copy'
                     '/jobshift/<ObjectId:jobshift_id>'
                     '/fromdate/<string:from_date_str>'
                     '/todate/<string:to_date_str>')

    # params - include_sunday, include_saturday
    api.add_resource(CopyAllJobshiftsHandler,
                     '/copy'
                     '/alljobshifts/for_date/<string:for_date_str>'
                     '/from_date/<string:from_date_str>'
                     '/to_date/<string:to_date_str>')

    api.add_resource(RoleHandler, '/employeeroles', endpoint='employeeroles')

    api.add_resource(HoursWorkedPerEmployeeHandler,
                     '/reporting'
                     '/hoursworkedperemployee'
                     '/from_date/<string:from_date_str>'
                     '/to_date/<string:to_date_str>')

    # params - from_date, to_date
    api.add_resource(HoursWorkedPerShiftRole,
                     '/reporting'
                     '/hoursworkedpershiftrole'
                     '/job/<ObjectId:job_id>')


    from views import views
    app.register_blueprint(views)

    app.handle_user_exception = api.handle_error


def enable_logging(app):
    formatter = logging.Formatter(
        'FOOOO%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    if app.debug:
        handler.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.ERROR)

    app.logger.addHandler(handler)


if __name__ == '__main__':

    env = os.environ.get(app_name.upper() + '_ENV', 'Production')
    config_object = ('config.%sConfig' % (env.capitalize(),))
    app = create_app(
        name=app_name,
        config_object=config_object
    )

    app.run()