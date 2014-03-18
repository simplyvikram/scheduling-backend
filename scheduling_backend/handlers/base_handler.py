
import datetime
from flask import request
from flask.ext.restful import Resource
from flask.ext.restful.reqparse import RequestParser

from scheduling_backend.models import BaseModel
from scheduling_backend.exceptions import UserException
from scheduling_backend.utils import (
    JsonUtils, DateUtils
)

class BaseHandler(Resource):

    POST = "POST"
    PUT = "PUT"
    GET = "GET"
    PATCH = "PATCH"


    def __init__(self, schema):

        super(BaseHandler, self).__init__()

        self.data = None
        self.schema = schema
        self.req_parser = RequestParser()

        if request.method in [BaseHandler.POST, BaseHandler.PATCH]:

            self.data = request.get_json(force=False, silent=True)

            # If data is not in json, mark it as an error
            if not self.data:
                raise UserException("Request is not in valid json format")

            # If validation fails, exception would be raised and that wouuld
            # be the end of the request
            JsonUtils.validate_json(self.data, self.schema)

            # We check if _id field is present inside post/put/patch. If it is
            # we mark it as an error, because id field is autogenerated and
            # cannot be modified
            self.req_parser.add_argument(BaseModel.Fields._ID,
                                         type=str,
                                         required=False,
                                         location='json',
                                         help="_id field cannot be modified")
            self.args = self.req_parser.parse_args()
            if self.args._id:
                raise UserException("_id field is autogenerated "
                                    "and cannot be present in request data")

        self.preprocess()

    def options(self, *args, **kwargs):

        headers_dict = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Max-Age': 1728000,
            'Access-Control-Allow-Methods': 'DELETE, GET, POST, PATCH',
            'Access-Control-Allow-Headers': 'accept, origin, content-type'
        }
        return "", 200, headers_dict

    def preprocess(self):

        if request.method == BaseHandler.GET:
            self.preprocess_GET()

        elif request.method == BaseHandler.POST:
            self.preprocess_POST()

        elif request.method == BaseHandler.PATCH:
            self.preprocess_PATCH()


    def preprocess_GET(self):
        pass

    def preprocess_POST(self):
        pass

    def preprocess_PATCH(self):
        pass


    def put(self):
        return {
            "error":
                "use patch instead, and only send fields which have changed"
        }


    def validate_start_and_end_dates(
            self, start_date_str, end_date_str
    ):
        """
        If end date is less than start date we raise an exception
        """
        if not start_date_str or not end_date_str:
            raise UserException("Start/end/from/to dates cannot be empty")

        start_date = DateUtils.to_datetime_format(start_date_str,
                                                  DateUtils.DATE)
        end_date = DateUtils.to_datetime_format(end_date_str,
                                                DateUtils.DATE)

        if (end_date - start_date).days < 0:
            raise UserException("Start/from date needs to be "
                                "less than end/to date")


    def validate_scheduled_start_and_end_times(
            self, scheduled_start_time_str, scheduled_end_time_str
    ):
        """
        If endtime is less than start time we raise an exception
        """

        if not scheduled_start_time_str or not scheduled_end_time_str:
            raise UserException("Scheduled start/end times cannot be empty")

        scheduled_start_time = DateUtils.to_datetime_format(
            scheduled_start_time_str, DateUtils.TIME
        )

        scheduled_end_time = DateUtils.to_datetime_format(
            scheduled_end_time_str, DateUtils.TIME
        )

        start = datetime.datetime(year=2012, month=1, day=1,
                                  hour=scheduled_start_time.hour,
                                  minute=scheduled_start_time.minute)
        end = datetime.datetime(year=2012, month=1, day=1,
                                hour=scheduled_end_time.hour,
                                minute=scheduled_end_time.minute)

        if (end - start).total_seconds() <= 0:
            raise UserException("Scheduled start time needs to be less than "
                                "scheduled end time")