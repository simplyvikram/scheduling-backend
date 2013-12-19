
from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.exceptions import UserException
from scheduling_backend.database_manager import DatabaseManager, Collection
from scheduling_backend.utils import DateUtils
from scheduling_backend.models import EmployeeShift, Job, JobShift, BaseModel

class DateHandler(BaseHandler):

    allowed_collections = ["jobshifts", "jobs", "employees"]

    def __init__(self):
        super(DateHandler, self).__init__(None)


    @marshaling_handler
    def get(self, collection_name, _date):

        # In case the leading zeros are not used with month or day
        _date = DateUtils.to_datetime_format(_date, DateUtils.DATE)
        _date = _date.isoformat()

        if collection_name not in DateHandler.allowed_collections:
            raise UserException("%s is not allowed" % collection_name)

        if collection_name == "employees":
            return DateHandler.get_all_employees_along_with_job_ids(_date)
        elif collection_name == "jobshifts":
            return DateHandler.get_jobshifts_for_date(_date)
        elif collection_name == "jobs":
            return DateHandler.get_jobs_for_date(_date)


    @staticmethod
    def get_jobs_for_date(_date):

        jobshifts = DateHandler.get_jobshifts_for_date(_date)
        job_ids = map(
            lambda jobshift: jobshift[JobShift.Fields.JOB_ID],
            jobshifts
        )

        if not job_ids:
            return {}

        query_dict = {
            BaseModel.Fields._ID: {'$in': job_ids}
        }
        jobs = DatabaseManager.find(
            Collection.JOBS,
            query_dict,
            multiple=True
        )
        return jobs


    @staticmethod
    def get_jobshifts_for_date(_date):

        query_dict = {JobShift.Fields.JOB_DATE: _date}
        jobshifts = DatabaseManager.find(
            Collection.JOBSHIFTS,
            query_dict,
            True
        )
        return jobshifts


    @staticmethod
    def get_all_employees_along_with_job_ids(_date):

        scheduled_employees = DateHandler.get_employees_for_date(_date)

        employee_ids = map(lambda x: x[EmployeeShift.Fields.EMPLOYEE_ID],
                           scheduled_employees)

        job_ids = map(lambda x: x[JobShift.Fields.JOB_ID],
                      scheduled_employees)

        all_employees = DatabaseManager.find(
            Collection.EMPLOYEES, {}, multiple=True
        )

        for employee in all_employees:
            employee[JobShift.Fields.JOB_ID] = None

            _id = employee[BaseModel.Fields._ID]

            if _id in employee_ids:
                index = employee_ids.index(_id)
                job_id = job_ids[index]
                employee[JobShift.Fields.JOB_ID] = job_id

        return all_employees


    @staticmethod
    def get_employees_for_date(_date):
        """
        Returns a list of elements. Each element contains an
        employee_id and job_id field representing an employee shift for
        the given date
        """
        # todo move this into database_manager module

        from flask import current_app
        d = current_app.db[Collection.JOBSHIFTS].aggregate(
            [
                {
                    '$match': {JobShift.Fields.JOB_DATE: _date}
                }
                ,
                {
                    '$project':
                        {
                            JobShift.Fields.EMPLOYEE_SHIFTS +
                            '.' + EmployeeShift.Fields.EMPLOYEE_ID: 1
                        }
                }
                ,
                {
                    '$unwind': '$' + JobShift.Fields.EMPLOYEE_SHIFTS
                }
                ,
                {
                    '$project':
                        {
                            EmployeeShift.Fields.EMPLOYEE_ID:
                                '$' + JobShift.Fields.EMPLOYEE_SHIFTS +
                                '.' + EmployeeShift.Fields.EMPLOYEE_ID,

                            JobShift.Fields.JOB_ID:
                                '$' + BaseModel.Fields._ID,

                            BaseModel.Fields._ID: 0
                        }
                }
            ]
        )
        # return {
        #     'ok': d['ok'],
        #     'result': d['result']
        # }
        # todo perhaps check what to return if d['ok'] is zero
        return d['result']