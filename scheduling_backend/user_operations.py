
import uuid
import hashlib

from scheduling_backend.database_manager import DatabaseManager, Collection
from scheduling_backend.models import User



class UserOperations(object):

    @staticmethod
    def create_user(username, password):
        """
        Throws an excpetion if a user with the same name exists
        """
        existing_user = UserOperations.find_user(username)
        if existing_user:
            raise Exception("Another user with the following name exists!")

        user = User(
            username,
            AuthenticationUtils.generate_passwordhash(password)
        )
        user_dict = User.encode(user)

        DatabaseManager.insert(
            User.USER_COLLECTION_NAME,
            user_dict
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


    @staticmethod
    def can_authenticate_user(username, passwordhash):

        query_dict = {
            User.Fields.USERNAME: username,
            User.Fields.PASSWORDHASH: passwordhash
        }

        document = DatabaseManager.find(
            User.USER_COLLECTION_NAME,
            query_dict,
            multiple=False
        )
        if document:
            return True
        else:
            return False


    # @staticmethod
    # def is_valid(username, password):
    #     query_dict = {
    #         User.Fields.USERNAME: username,
    #         User.Fields.PASSWORDHASH:
    #             AuthenticationUtils.generate_password_hash(password)
    #     }
    #     found_user = DatabaseManager.find(
    #         User.USER_COLLECTION_NAME, query_dict=query_dict, multiple=False
    #     )
    #     if found_user:
    #         return True
    #     else:
    #         return False


class AuthenticationUtils(object):

    @staticmethod
    def generate_passwordhash(password):

        # salt = uuid.uuid4().hex
        salt = "vikram singh"
        passwordhash = hashlib.sha512(password + salt).hexdigest()
        return passwordhash




