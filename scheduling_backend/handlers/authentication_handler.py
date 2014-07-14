
from scheduling_backend.handlers import BaseHandler, marshaling_handler
from scheduling_backend.user_operations import (
    UserOperations,
    AuthenticationUtils
)
from scheduling_backend.models import User
from scheduling_backend.exceptions import UserException
from scheduling_backend.json_schemas import schema_user_login



# caution
# we should have json schema etc for this but no time

class LoginHandler(BaseHandler):

    def __init__(self):
        super(LoginHandler, self).__init__(schema_user_login)


    @marshaling_handler
    def post(self):


        print "Inside login handler"
        print "self.data.get", self.data.get

        try:
            username = self.data.get('username')
            password = self.data.get('password')

            passwordhash = AuthenticationUtils.generate_passwordhash(password)
            can_authenticate_user = UserOperations.can_authenticate_user(
                username=username,
                passwordhash=passwordhash
            )
            if not can_authenticate_user:
                raise UserException('Cannot authenticate user')
            else:
                return {
                    User.Fields.USERNAME: username,
                    User.Fields.PASSWORDHASH: passwordhash
                }

        except Exception as e:
            raise UserException(e.message)