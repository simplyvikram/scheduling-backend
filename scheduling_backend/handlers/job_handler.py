
import datetime

from flask import current_app as current_app
from flask import g

from flask.ext.restful import Resource
import flask.ext.restful
import flask.ext.restful.types

from scheduling_backend.utils import DateUtils
from scheduling_backend.exceptions import UserException
from scheduling_backend.models import Job, JobShift
from scheduling_backend.handlers import Params, marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_job


class JobHandler(BaseHandler):

    def __init__(self):
        super(JobHandler, self).__init__(schema_job)

    def preprocess(self):

        self.req_parser.add_argument(Params.INCLUDE_JOBSHIFTS,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     default=False,
                                     required=False)

        # self.req_parser.add_argument(Params.INCLUDE_EMPLOYEESHIFTS,
        #                              type=flask.ext.restful.types.boolean,
        #                              location='args',
        #                              default=False,
        #                              required=False)



        self.args = self.req_parser.parse_args()
        # print "self. args --- ", self.args
        # print "request. args-----", request.view_args

        super(JobHandler, self).preprocess()


    def preprocess_POST(self):
        pass

    def preprocess_GET(self):
        pass

    def preprocess_PATCH(self):
        pass

    def get(self, job_id=None):

        if not job_id and self.args.get(Params.INCLUDE_JOBSHIFTS, None):
            raise UserException("Inclusion of job shifts not allowed for this"
                                "operation")

        if job_id:
            # Find the job with the matching _id
            job = current_app.db.jobs.find_one({"_id": job_id})
            if job is None:
                return {}

            if self.args.get(Params.INCLUDE_JOBSHIFTS, None):
                self._append_jobshift_to_job_response(job)
            return job

        else:
            # find all jobs
            jobs_cursor = current_app.db.jobs.find()
            jobs_list = list(jobs_cursor)

            return jobs_list


    # @common_handler
    @marshaling_handler
    def post(self):
        # We create a job object to make sure we have all the data we need
        # to create a job, if not an exception will be raised

        job = Job(**self.data)

        self.validate_start_and_end_dates(job.start_date,
                                          job.end_date)
        self.validate_scheduled_start_and_end_times(job.scheduled_start_time,
                                                    job.scheduled_end_time)

        # todo sort out the sat/sun part later
        date_list = DateUtils.get_dates_in_range(job.start_date, job.end_date,
                                                 include_saturday=True,
                                                 include_sunday=True)

        job_id = self._create_job(job)
        self._create_jobshifts(job_id, date_list,
                               job.scheduled_start_time,
                               job.scheduled_end_time)

        job_dict = current_app.db.jobs.find_one({"_id": job_id})

        if self.args.get(Params.INCLUDE_JOBSHIFTS, None):
            self._append_jobshift_to_job_response(job_dict)

        return job_dict


    @marshaling_handler
    def patch(self, job_id):

        job_dict = current_app.db.jobs.find_one({"_id": job_id})
        if not job_dict:
            raise UserException("Invalid job id")

        found_job = Job(**job_dict)
        g.job = found_job

        _dict = self.data

        new_start_date = _dict.get(Job.Fields.START_DATE,
                                   found_job.start_date)
        new_end_date = _dict.get(Job.Fields.END_DATE,
                                 found_job.end_date)

        new_scheduled_start_time = _dict.get(Job.Fields.SCHEDULED_START_TIME,
                                             found_job.scheduled_start_time)
        new_scheduled_end_time = _dict.get(Job.Fields.SCHEDULED_END_TIME,
                                           found_job.scheduled_end_time)

        self.validate_start_and_end_dates(new_start_date, new_end_date)
        self.validate_scheduled_start_and_end_times(new_scheduled_start_time,
                                                    new_scheduled_end_time)

        # make all the necessary patch changes
        current_app.db.jobs.update({"_id": job_id}, {'$set': _dict})
        self._modify_jobshifts_dates(job_id, new_start_date, new_end_date)
        self._modify_jobshifts_times(job_id,
                                     new_scheduled_start_time,
                                     new_scheduled_end_time)

        # not retrieve all the information about the job and send it back
        job_dict = current_app.db.jobs.find_one({"_id": job_id})
        if self.args.get(Params.INCLUDE_JOBSHIFTS, None):
            self._append_jobshift_to_job_response(job_dict)

        return job_dict


    def _create_job(self, job):
        job_id = current_app.db.jobs.insert(Job.encode(job))
        return job_id


    def _create_jobshifts(self, job_id, date_list,
                          scheduled_start_time_str,
                          scheduled_end_time_str):
        jobshifts = []
        for d in date_list:
            jobshift = JobShift(job_id=job_id,
                                job_date=d.isoformat(),
                                scheduled_start_time=scheduled_start_time_str,
                                scheduled_end_time=scheduled_end_time_str)
            jobshifts.append(JobShift.encode(jobshift))

        if not jobshifts:
            return

        current_app.db.jobshifts.insert(jobshifts)


    def _get_dates_to_add_and_remove(self, old_start_date, old_end_date,
                                     new_start_date, new_end_date):
        # todo comment this damn thing at some point to explain whats going on

        dates_to_add = set()
        dates_to_remove = set()

        start_delta = (new_start_date - old_start_date).days
        if start_delta > 0:
            # this means the job is starting at a later date
            for i in range(0, start_delta):
                dates_to_remove.add(old_start_date + datetime.timedelta(days=i))
        else:
            # this means that the job is starting at an earlier date
            # start_delta is negative
            for i in range(-1, start_delta - 1, -1):
                dates_to_add.add(old_start_date + datetime.timedelta(days=i))

        end_delta = (new_end_date - old_end_date).days
        if end_delta > 0:
            # this means that the job is finishing at a later date
            for i in range(1, end_delta + 1):
                dates_to_add.add(old_end_date + datetime.timedelta(days=i))
        else:
            # this means that the job is finishing at an earlier date
            for i in range(0, end_delta, -1):
                dates_to_remove.add(old_end_date + datetime.timedelta(days=i))

        common_elements = set.intersection(set(dates_to_add),
                                           set(dates_to_remove))
        map(lambda x: dates_to_add.remove(x) or dates_to_remove.remove(x),
            common_elements)

        print "\n\n\ndates_to_add", dates_to_add
        print "\n\n\ndates_to_remove", dates_to_remove

        return dates_to_add, dates_to_remove


    def _modify_jobshifts_dates(self, job_id, new_start_date, new_end_date):

        if (new_start_date == g.job.start_date and
                    new_end_date == g.job.end_date):
            # If nothing has changed we just return
            return

        old_start_date = DateUtils.to_datetime_format(g.job.start_date,
                                                      DateUtils.DATE)
        old_end_date = DateUtils.to_datetime_format(g.job.end_date,
                                                    DateUtils.DATE)

        new_start_date = DateUtils.to_datetime_format(new_start_date,
                                                      DateUtils.DATE)
        new_end_date = DateUtils.to_datetime_format(new_end_date,
                                                    DateUtils.DATE)

        dates_to_add, dates_to_remove = self._get_dates_to_add_and_remove(
            old_start_date, old_end_date,
            new_start_date, new_end_date
        )

        dates_to_remove = map(lambda x: x.isoformat(), dates_to_remove)
        current_app.db.jobshifts.remove(
            {
                JobShift.Fields.JOB_ID: job_id,
                JobShift.Fields.JOB_DATE: {"$in": dates_to_remove}
            },
            justOne=False
        )
        # We still use the old scheduled start and end times here to create
        # job shifts. If the scheduled start and end times need to be changed
        # they are changed elsewhere
        self._create_jobshifts(job_id, dates_to_add,
                               g.job.scheduled_start_time,
                               g.job.scheduled_end_time)


    def _modify_jobshifts_times(self, job_id,
                                new_scheduled_start_time,
                                new_scheduled_end_time):
        if (new_scheduled_start_time == g.job.scheduled_start_time and
                    new_scheduled_end_time == g.job.scheduled_end_time):
            return

        current_app.db.jobshifts.update(
            {JobShift.Fields.JOB_ID: job_id},
            {"$set": {
                JobShift.Fields.SCHEDULED_START_TIME: new_scheduled_start_time,
                JobShift.Fields.SCHEDULED_END_TIME: new_scheduled_end_time}},
            multi=True,
            upsert=False
        )


    def _append_jobshift_to_job_response(self, job_dict):

        jobshifts = current_app.db.jobshifts.find(
            {JobShift.Fields.JOB_ID: job_dict["_id"]}
        )

        jobshifts = list(jobshifts)
        job_dict["jobshifts"] = jobshifts


    def delete(self, job_id):

        # todo what if the first delete fails. Oh shitttt ;-)
        result = current_app.db.jobshifts.remove(
            {JobShift.Fields.JOB_ID: job_id},
            justOne=False
        )
        result = current_app.db.jobs.remove({"_id": job_id})

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404