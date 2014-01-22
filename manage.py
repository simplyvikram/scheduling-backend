
import os

from flask_script import Manager, Server, Option
from flask_script.commands import Command

from scheduling_backend import app_name, create_app

env = os.environ.get(app_name.upper() + '_ENV', 'Production')
config_object = '%s.config.%sConfig' % (app_name, env.capitalize())


app = create_app(
    name=app_name,
    config_object=config_object,
)

manager = Manager(app)


@manager.command
def hello():
    """
    Just print whatever
    """
    print "Whatever"


class GunicornServer(Command):

    description = 'Run the app within Gunicorn'

    # only use 0.0.0.0 and not localhost or 127.0.0.1 as 0.0.0.0 makes it
    # globally accessible by all ipv4 addresses
    def __init__(self, host='0.0.0.0', port=5000, workers=4):
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
                return {
                    'bind': '{0}:{1}'.format(host, port),
                    'workers': workers
                }

            def load(self):
                return app

        FlaskApplication().run()


manager.add_command("run-server", Server(host='0.0.0.0', port=5000))
manager.add_command('run-gunicorn-server', GunicornServer())


if __name__ == '__main__':
    manager.run()