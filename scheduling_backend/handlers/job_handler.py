from flask.ext.restful import Resource
from flask import request
from flask import current_app as current_app

from scheduling_backend.utils import (
    DateUtils,
)
from scheduling_backend.models import Job
from scheduling_backend.handlers import object_id_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_job


class JobHandler(BaseHandler):

    def __init__(self):
        super(JobHandler, self).__init__(schema_job)

    def preprocess_data(self, data):
        start_date = data.get(Job.Tag.START_DATE, None)
        end_date = data.get(Job.Tag.END_DATE, None)

        for d in [start_date, end_date]:
            self.error = DateUtils.validate(d, DateUtils.DATE)
            if self.error:
                return


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

        job_id = current_app.db.jobs.insert(self.data)
        job = current_app.db.jobs.find_one({"_id": job_id})

        return job


    @object_id_handler
    def patch(self, job_id):

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

