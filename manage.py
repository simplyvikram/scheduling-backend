
import os

from flask_script import Manager, Server

from scheduling_backend import app_name, create_app

env = os.environ.get(app_name.upper() + '_ENV', 'Production')
config_object = '%s.config.%sConfig' % (app_name, env.capitalize())


app = create_app(
    name=app_name,
    config_object=config_object,
)

manager = Manager(app)
manager.add_command("runserver", Server())


@manager.command
def hello():
    print "Whatever"

if __name__ == '__main__':
    manager.run()