
import uuid
import hashlib


from scheduling_backend.database_manager import DatabaseManager, Collection
from scheduling_backend.exceptions import UserException
from scheduling_backend.models import User




class UserOperations(object):

    @staticmethod
    def create_user(username, password, name):
        """
        Throws an excpetion if a user with the same name exists
        """
        existing_user = UserOperations.find_user(username)
        if existing_user:
            raise Exception("Another user with the following name exists!")

        passwordhash = AuthenticationUtils.generate_passwordhash(password)
        user = User(
            username=username, passwordhash=passwordhash, name=name
        )
        user_dict = User.encode(user)

        DatabaseManager.insert(
            User.USER_COLLECTION_NAME,
            user_dict
        )


    # todo merge the two methods to find user, make password optional
    @staticmethod
    def find_user_with_passwordhash(username, passwordhash):
        query = {
            User.Fields.USERNAME: username,
            User.Fields.PASSWORDHASH: passwordhash
        }
        user_dict = DatabaseManager.find(
            User.USER_COLLECTION_NAME, query_dict=query, multiple=False
        )

        if user_dict:
            return User(**user_dict)
        else:
            return None

    @staticmethod
    def update_user(username, passwordhash, _dict):
        """
        Updates user with the dict, and returns the updated user
        """

        user = UserOperations.find_user_with_passwordhash(
            username, passwordhash
        )
        if not user:
            raise UserException('Could not find user')

        if len(_dict.keys()) == 0:
            return user

        query_dict = {
            User.Fields.USERNAME: username,
            User.Fields.PASSWORDHASH: passwordhash
        }
        update_dict = {
            "$set": _dict
        }

        DatabaseManager.update(
            User.USER_COLLECTION_NAME,
            query_dict,
            update_dict,
            multi=False, upsert=False
        )

        return UserOperations.find_user_with_passwordhash(
            username, passwordhash
        )


    @staticmethod
    def find_user(username):
        """
        Returns none if no user found with the given username
        else return the user object
        """
        query = {
            User.Fields.USERNAME: username
        }
        user_dict = DatabaseManager.find(
            User.USER_COLLECTION_NAME, query, multiple=False
        )
        if user_dict:
            return User(**user_dict)

    @staticmethod
    def update_user_password(username, password):

        found_user = UserOperations.find_user(username)
        if not found_user:
            raise Exception("Could not find user with username %s"
                            % (username,))

        query_dict = {
            User.Fields.USERNAME: username
        }
        update_dict = {
            '$set': {
                User.Fields.PASSWORDHASH:
                    AuthenticationUtils.generate_passwordhash(password)
            }
        }

        DatabaseManager.update(
            User.USER_COLLECTION_NAME,
            query_dict=query_dict,
            update_dict=update_dict,
            multi=False,
            upsert=False
        )


class AuthenticationUtils(object):

    @staticmethod
    def generate_passwordhash(password):

        # salt = uuid.uuid4().hex
        salt = "vikram singh"
        passwordhash = hashlib.sha512(password + salt).hexdigest()
        return passwordhash