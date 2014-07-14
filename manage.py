
import os

from flask_script import Manager, Server, Option
from flask_script.commands import Command
from flask_sslify import SSLify

from scheduling_backend import app_name, create_app
from scheduling_backend.user_operations import (
    UserOperations, AuthenticationUtils
)


# ssl_key_path = '/Users/vikram/voyager_2013/flask_projects/scheduling-backend/localhost.key'
# ssl_crt_path = '/Users/vikram/voyager_2013/flask_projects/scheduling-backend/localhost.crt'
ssl_key_path = 'localhost.key'
ssl_crt_path = 'localhost.crt'


from OpenSSL import SSL
ssl_context = SSL.Context(SSL.SSLv23_METHOD)
ssl_context.use_privatekey_file(ssl_key_path)
ssl_context.use_certificate_file(ssl_crt_path)

env = os.environ.get(app_name.upper() + '_ENV', 'Production')
config_object = '%s.config.%sConfig' % (app_name, env.capitalize())


app = create_app(
    name=app_name,
    config_object=config_object,
)

# sslify = SSLify(app, permanent=True)

manager = Manager(app)


@manager.command
def hello():
    """
    Just print whatever
    """
    print "Whatever"

class CreateUser(Command):

    description = "create_user -u username -p password"
    option_list = (
        Option('--username', '-u', dest='username', required=True),
        Option('--password', '-p', dest='password', required=True)
    )

    def run(self, username, password):
        print "Inside createUser username <%s>" % (username,)
        print "Inside createUser password <%s>" % (password,)

        password_hash = password
        UserOperations.create_user(username, password_hash)

        print "Created a user <%s>" % (username,)

class UpdateUserPassword(Command):

    description = "update_user_password -u username -np new_password"
    option_list = (
        Option('--username', '-u', dest='username', required=True),
        Option('--new_password', '-np', dest='new_password', required=True)
    )

    def run(self, username, new_password):
        print "Inside update_user_password username <%s>" % (username,)
        print "Inside update_user_password new_password <%s>" % (new_password,)

        UserOperations.update_user_password(username, new_password)

        print "Updated user <%s>" % (username,)

class GunicornServer(Command):

    description = 'Run the app within Gunicorn'

    # only use 0.0.0.0 and not localhost or 127.0.0.1 as 0.0.0.0 makes it
    # globally accessible by all ipv4 addresses
    def __init__(self, host='0.0.0.0', port=5000, workers=4,
                 ):
        self.port = port
        self.host = host
        self.workers = workers




    def get_options(self):
        return (
            Option('-H', '--host',
                   dest='host',
                   default=self.host),

            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port),

            Option('-w', '--workers',
                   dest='workers',
                   type=int,
                   default=self.workers),
        )

    def handle(self, app, host, port, workers):

        from gunicorn.app.base import Application

        class FlaskApplication(Application):
            def init(self, parser, opts, args):

                # todo for some reason there is no stack trace for gunicorn
                # debug flag doesnt seem to do the trick,
                # keeping it there for now
                # use default flask server to see trace
                d = {
                    'bind': '{0}:{1}'.format(host, port),
                    'workers': workers,
                    'debug': True,
                    'keyfile': ssl_key_path,
                    'certfile': ssl_crt_path
                }

                return d

            def load(self):
                return app

        FlaskApplication().run()


@manager.command
def run_server():
    app.run(host='localhost', port=4333, debug=True,
            ssl_context=ssl_context)

@manager.command
def run_server_unsecure():
    app.run(host='localhost', port=4333, debug=True)


manager.add_command(
    'run_gunicorn_server',
    GunicornServer(host='127.0.0.1', port=4333)
)
manager.add_command('create_user', CreateUser())
manager.add_command('update_user_password', UpdateUserPassword())


if __name__ == '__main__':
    manager.run()