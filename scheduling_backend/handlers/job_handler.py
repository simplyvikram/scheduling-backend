from flask.ext.restful import Resource

class JobHandler(Resource):

    def get(self):
        return {'get': 'nothing'}

    def post(self):
        return {'post': 'nothing'}

    def put(self):
        return {'put': 'nothing'}

    def patch(self):
        return {'patch': 'nothing'}
