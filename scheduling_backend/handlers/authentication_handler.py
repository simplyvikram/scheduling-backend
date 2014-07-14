
from flask import request
from flask.ext.restful.reqparse import RequestParser

from scheduling_backend.handlers import BaseHandler, authentication_handler
from scheduling_backend.user_operations import (
    UserOperations,
    AuthenticationUtils
)
from scheduling_backend.exceptions import UserException
from scheduling_backend.json_schemas import schema_user_login
from scheduling_backend.models import User, BaseModel


def remove_id_from_user_dict(user_dict):

    del user_dict[BaseModel.Fields._ID]
    return user_dict


class LoginHandler(BaseHandler):

    def __init__(self):
        super(LoginHandler, self).__init__(schema_user_login)


    def post(self):
        try:
            username = self.data.get('username')
            password = self.data.get('password')

            passwordhash = AuthenticationUtils.generate_passwordhash(password)

            user = UserOperations.find_user_with_passwordhash(
                username=username, passwordhash=passwordhash)

            if not user:
                return "Cannot authenticate user", 401
                # raise UserException('Cannot authenticate user')


            user_dict = User.encode(user)
            user_dict = remove_id_from_user_dict(user_dict)

            return user_dict, 200

        except Exception as e:
            raise UserException(e.message)



class UpdateUserHandler(BaseHandler):

    def __init__(self):
        super(UpdateUserHandler, self).__init__(None)

    @authentication_handler
    def get(self):

        params_parser = RequestParser()

        params_parser.add_argument(User.Fields.NAME,
                            type=str,
                            required=False,
                            location='args')

        params_parser.add_argument(User.Fields.SETTINGS,
                            type=str,
                            required=False,
                            location='args')

        fields = params_parser.parse_args()

        name = fields.get(User.Fields.NAME, None)
        settings = fields.get(User.Fields.SETTINGS, None)

        d = dict()
        if name is not None:
            d[User.Fields.NAME] = name
        if settings is not None:
            d[User.Fields.SETTINGS] = settings


        updated_user = UserOperations.update_user(
            request._username, request._passwordhash, d
        )

        user_dict = User.encode(updated_user)
        user_dict = remove_id_from_user_dict(user_dict)
        return user_dict