
from flask import Blueprint
from flask import current_app as c_app

views = Blueprint('views', __name__, url_prefix='')


@views.route('/testenv', methods=['GET'])
def testenv():
    from scheduling_backend import app_name
    import os
    env_var_name = app_name.upper() + '_ENV'
    env_var_value = os.environ[env_var_name]

    result = "<br><br> env_var_name - " + env_var_name
    result += "<br><br> env_var_value - " + env_var_value
    result = "<br><br> app.debug - " + str(c_app.debug)
    result += "<br><br> app.testing -  " + str(c_app.testing)
    result += "<br><br> app.mongodb_uri -  " + str(c_app.config['MONGODB_URI'])
    # result += "<br><br> app.mongodb_name -  " + str(app.mongodb_name)
    result += "<br><br> app.db - " + str(c_app.db)

    result += "<br><br>"
    result += "<table>"
    # for model, schema in schemas.iteritems():
    #     result += "<tr>"
    #     result += "<td><p>" + model + "_schema</p></td>"
    #     result += "<td><p>" + schema + "</p></td>"
    #     result += "</tr>"
    #     result += "<br>"
    # result += "</table>"
    return result


@views.route('/foo', methods=['GET'])
def foo():
    from random import randint
    from datetime import datetime
    post = {'timestamp': datetime.now(),
            'random_number': randint(1, 100)}
    c_app.db.posts.insert(post)
    return "Just inserted - %s" % (str(post),)


@views.route('/bar', methods=['GET'])
def bar():

    result = '<br>'
    for post in c_app.db.posts.find():
        result += '<br>' + str(post)

    return result

@views.route('/foobar', methods=['GET'])
def foobar():

    c_app.db.posts.remove()
    result = '<br>'
    for post in c_app.db.posts.find():
        result += '<br>' + str(post)

    return result