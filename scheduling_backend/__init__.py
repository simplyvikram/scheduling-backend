
import logging
import os
import sys

from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask import abort, Flask
from flask.ext.restful import Api
from pymongo import MongoClient
from werkzeug.routing import BaseConverter, ValidationError

app_name = 'scheduling_backend'


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

    api.add_resource(JobHandler, '/jobs')
    # api.add_resource(ClientHandler, '/clients/<string:_id>')
    api.add_resource(ClientHandler, '/clients/<ObjectId:obj_id>',
                     endpoint="client")

    api.add_resource(ClientHandler, '/clients', endpoint="clients")

    from views import views
    app.register_blueprint(views)


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