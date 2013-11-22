
import logging
import os
import sys

from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask import abort, Flask, request
from flask.ext.restful import Api
from pymongo import MongoClient
from werkzeug.routing import BaseConverter, ValidationError

app_name = 'scheduling_backend'

global the_context


class BsonObjectIdConverter(BaseConverter):
    """
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
    api = Api(app)

    app.url_map.converters['ObjectId'] = BsonObjectIdConverter

    from handlers.job_handler import JobHandler
    from handlers.client_handler import ClientHandler
    from handlers.employee_handler import EmployeeHandler
    from handlers.jobshift_handler import JobShiftHandler
    from handlers.employeeshift_handler import EmployeeShiftHandler
    from handlers import RoleHandler

    api.add_resource(ClientHandler, '/clients/<ObjectId:obj_id>',
                     endpoint="client")
    api.add_resource(ClientHandler, '/clients', endpoint="clients")


    api.add_resource(EmployeeHandler, '/employees/<ObjectId:obj_id>',
                     endpoint="employee")
    api.add_resource(EmployeeHandler, '/employees', endpoint="employees")


    # for jobs, include a parameter to include jobshifts, jobshifts_ids/jobshifts
    api.add_resource(JobHandler, '/jobs/<ObjectId:job_id>', endpoint="job")
    api.add_resource(JobHandler, '/jobs', endpoint="jobs")



    # GET
    # DELETE, delete would also delete associated employee shifts
    # No POST, jobshifts are created while creating/changing jobs
    # PATCH would change a job shift
    api.add_resource(JobShiftHandler,
                     '/jobshifts/<ObjectId:jobshift_id>',
                     endpoint="jobshift")
    api.add_resource(JobShiftHandler,
                     '/jobshifts',
                     endpoint="jobsshifts")

    # # # POST with no data, returns created Employee Shift
    # api.add_resource('/jobshifts/<ObjectId:job_shift_id>'
    #                  '/employee/<ObjectId:employee_id>',
    #                  endpoint="createemployeeshift")


    # GET, employee shifts have post
    # PATCH, return modified employee shift
    # DELETE, removes employeeshift from jobshift
    api.add_resource(EmployeeShiftHandler,
                     '/employeeshifts/<ObjectId:employee_shift_id>',
                     endpoint="employeeshift")


    # POST with no data to create an employeeshift todo maybe a new handler
    api.add_resource(JobShiftHandler,
                     '/addemployeeshift'
                     '/jobshifts/<ObjectId:jobshift_id>'
                     '/employee/<ObjectId:employee_id>',

                     endpoint="create_employee_shift")

    # todo finish url for copy job shifts
    # api.add_resource(JobShiftHandler,
    #                  '/copyjobshift/<ObjectId:jobshift_id')
    #
    # post_copy_job_shifts = 'jobshift/<ObjectId:jobshift_id>/copy'
    # post_copy_job_shifts_params = '?' + 'fromdate' + '=XXXX' + '&' + 'todate' + '=YYY'



    api.add_resource(RoleHandler, '/employeeroles', endpoint='employeeroles')

    from views import views
    app.register_blueprint(views)

    # @app.before_request
    # def before(*args, **kwargs):
    #     data = request.get_json(force=False, silent=True)
    #     if data:
    #         print "Before request - type:%s data:%s" % (type(data), data)
    #     else:
    #         print "Before reqquest - data is none"
    #
    # @app.after_request
    # def after(response):
    #     data = response.data
    #     if data:
    #         print "After request - data", str(data)
    #     else:
    #         print "After request - data is none"
    #
    #     return response

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