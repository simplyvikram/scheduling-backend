from flask.ext.restful import Resource
from flask import request
from flask import current_app as current_app

from scheduling_backend.utils import (
    DateUtils,
    JsonUtils
)
from scheduling_backend.models import Job
from scheduling_backend.handlers import MessageDict, object_id_handler
from scheduling_backend.json_schemas import schema_job


class JobHandler(Resource):

    def __init__(self):
        super(JobHandler, self).__init__()

        self.data = None
        self.error = None

        if request.method in ["PUT", "POST", "PATCH"]:

            self.data = request.get_json(force=False, silent=False)

            # If data is not in json, mark it as an error
            print "Inside job init - data  type:%s, data:%s" % \
                  (type(self.data), self.data)

            if not self.data:
                self.error = MessageDict.request_not_in_json
            else:
                self.error = JsonUtils.validate_json(self.data, schema_job)

            if self.error:
                return

            self.validate_data(self.data)


    def validate_data(self, data):
        start_date = data.get(Job.tag_start_date, None)
        end_date = data.get(Job.tag_start_date, None)

        for d in [start_date, end_date]:
            self.error = DateUtils.validate(d, DateUtils.DATE)
            if self.error:
                return


    def transform_data(self):
        # todo do we need this?
        pass


    @object_id_handler
    def get(self, job_id=None):

        if job_id:
            job = current_app.db.jobs.find_one({"_id": job_id})
            print "Inside get", job
            if job is None:
                return {}

            return job

        else:
            jobs_cursor = current_app.db.jobs.find()
            jobs_list = list(jobs_cursor)

            return jobs_list


    @object_id_handler
    def post(self):
        if self.error:
            return self.error

        print "Received DATA, type:%s, data:%s" % (type(self.data), self.data)

        job_id = current_app.db.jobs.insert(self.data)
        job = current_app.db.jobs.find_one({"_id": job_id})

        return job


    @object_id_handler
    def patch(self, job_id):
        if self.error:
            return self.error

        current_app.db.jobs.update({"_id": job_id}, {'$set': self.data})

        job = current_app.db.jobs.find_one({"_id": job_id})
        print "jobId type:%s value:%s" % (type(job_id), job_id)
        return job


    def delete(self, job_id):
        # todo can the data have an array of jobs to be deleted????
        result = current_app.db.jobs.remove({"_id": job_id})

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404

