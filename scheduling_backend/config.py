
class Config(object):
    pass


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MONGODB_URI = '!!!!CHANGE ME!!!!'
    MONGODB_NAME = '!!!!CHANGE ME!!!!'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/'
    MONGODB_NAME = 'test_db'
