import urlparse
from bson.objectid import ObjectId, InvalidId

from flask.ext.restful import Resource
from flask import request
# from flask.ext.restful import reqparse
from flask import current_app as current_app

from scheduling_backend.utils import (
    DateUtils,
)
from scheduling_backend.models import Job, JobShift, tag_id
from scheduling_backend.handlers import common_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_job


class JobHandler(BaseHandler):


    def __init__(self):
        super(JobHandler, self).__init__(schema_job)

    def preprocess_data(self, data):

        if self.error:
            return

        if request.method == BaseHandler.PATCH:
            self._validate_patch_data()
        elif request.method == BaseHandler.POST:
            self._validate_post_data()

    def _validate_patch_data(self):

        if self.error:
            return

        self.validate_str_field(Job.Tag.LOCATION, False)
        self.validate_str_field(Job.Tag.NAME, False)

        self.validate_str_as_object_id_field(Job.Tag.CLIENT_ID, False)

        self.validate_date_time_field(Job.Tag.START_DATE, DateUtils.DATE, False)
        self.validate_date_time_field(Job.Tag.END_DATE, DateUtils.DATE, False)
        self.validate_date_time_field(Job.Tag.SCHEDULED_START_TIME,
                                      DateUtils.TIME, False)
        self.validate_date_time_field(Job.Tag.SCHEDULED_END_TIME,
                                      DateUtils.TIME, False)

        if self.error:
            return


    def _validate_post_data(self):

        if self.error:
            return

        client_id = self.data.get(Job.Tag.CLIENT_ID, None)
        name = self.data.get(Job.Tag.NAME, None)
        location = self.data.get(Job.Tag.LOCATION, None)

        start_date = self.data.get(Job.Tag.START_DATE, None)
        end_date = self.data.get(Job.Tag.END_DATE, None)
        scheduled_start_time = self.data.get(Job.Tag.SCHEDULED_START_TIME, None)
        scheduled_end_time = self.data.get(Job.Tag.SCHEDULED_END_TIME, None)

        l = [client_id, name, location,
             start_date, end_date,
             scheduled_start_time, scheduled_end_time]

        is_any_field_missing = BaseHandler.none_present_in_list(l)

        if is_any_field_missing:
            self.error = {"error": "Missing required field"}
            return

        self._validate_patch_data()

    @common_handler
    def get(self, job_id=None):

        # Find the job shifts associated with this job
        lastfield = urlparse.urlparse(request.base_url).path.split('/')[-1]
        if lastfield == 'jobshifts':
            return self._find_job_fields(job_id)

        if job_id:
            # Find the job with the matching _id
            job = current_app.db.jobs.find_one({"_id": job_id})
            if job is None:
                return {}

            return job

        else:
            # find all jobs
            jobs_cursor = current_app.db.jobs.find()
            jobs_list = list(jobs_cursor)

            return jobs_list


    @common_handler
    def post(self):

        job_id = current_app.db.jobs.insert(self.data)
        job = current_app.db.jobs.find_one({"_id": job_id})

        # job_id = job.get(tag_id, None)

        # todo create the jobshifts

        # job["_type"] = str(type(job_id))
        # job["_value"] = str(job_id)

        return job


    @common_handler
    def patch(self, job_id):

        current_app.db.jobs.update({"_id": job_id}, {'$set': self.data})

        # todo, modify appropriate job shifts as needed

        job = current_app.db.jobs.find_one({"_id": job_id})

        return job


    def delete(self, job_id):
        # todo can the data have an array of jobs to be deleted????
        result = current_app.db.jobs.remove({"_id": job_id})

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404


    def _find_job_fields(self, job_id):
        return {"IMPLEMENT ME!!!": True,
                "jobfields for jobId %s" % str(job_id): []}
