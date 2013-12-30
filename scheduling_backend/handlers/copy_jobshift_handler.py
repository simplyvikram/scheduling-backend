
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.handlers import marshaling_handler, Params
from scheduling_backend.models import BaseModel, Job, JobShift, EmployeeShift
from scheduling_backend.database_manager import (
    DatabaseManager, Collection, JobOperations
)
from scheduling_backend.utils import DateUtils

import flask.ext.restful.types


class CopyJobshiftHandler(BaseHandler):

    def __init__(self):
        super(CopyJobshiftHandler, self).__init__(None)

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.INCLUDE_SATURDAY,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     required=False)
        self.req_parser.add_argument(Params.INCLUDE_SUNDAY,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     required=False)

        self.args = self.req_parser.parse_args()


    def get(self, jobshift_id, from_date_str, to_date_str):

        include_saturday = self.args.get(Params.INCLUDE_SATURDAY, False)
        include_sunday = self.args.get(Params.INCLUDE_SUNDAY, False)

        from_date_str = DateUtils.to_datetime_format(from_date_str,
                                                     DateUtils.DATE).isoformat()
        to_date_str = DateUtils.to_datetime_format(to_date_str,
                                                   DateUtils.DATE).isoformat()

        # making sure that to_date is later or same as from_date
        self.validate_start_and_end_dates(from_date_str, to_date_str)

        copy_jobshift_contents(
            jobshift_id, from_date_str, to_date_str, include_saturday, include_sunday
        )

        return '', 204


class CopyAllJobshiftsHandler(BaseHandler):

    def __init__(self):
        super(CopyAllJobshiftsHandler, self).__init__(None)

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.INCLUDE_SATURDAY,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     required=False)
        self.req_parser.add_argument(Params.INCLUDE_SUNDAY,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     required=False)

        self.args = self.req_parser.parse_args()


    def get(self, for_date_str, from_date_str, to_date_str):

        include_saturday = self.args.get(Params.INCLUDE_SATURDAY, False)
        include_sunday = self.args.get(Params.INCLUDE_SUNDAY, False)

        for_date_str = DateUtils.to_datetime_format(for_date_str,
                                                    DateUtils.DATE).isoformat()
        from_date_str = DateUtils.to_datetime_format(from_date_str,
                                                     DateUtils.DATE).isoformat()
        to_date_str = DateUtils.to_datetime_format(to_date_str,
                                                   DateUtils.DATE).isoformat()

        self.validate_start_and_end_dates(from_date_str, to_date_str)

        jobshift_ids = JobOperations.find_jobshift_ids_for_day(for_date_str)

        for jobshift_id in jobshift_ids:
            copy_jobshift_contents(jobshift_id,
                                   from_date_str,
                                   to_date_str,
                                   include_saturday,
                                   include_sunday)

        return '', 204


def copy_jobshift_contents(jobshift_id,
                           from_date_str,
                           to_date_str,
                           include_saturday,
                           include_sunday):

    jobshift = DatabaseManager.find_document_by_id(
        Collection.JOBSHIFTS, jobshift_id, True
    )

    job_id = jobshift[JobShift.Fields.JOB_ID]
    scheduled_start_time = jobshift[JobShift.Fields.SCHEDULED_START_TIME]
    scheduled_end_time = jobshift[JobShift.Fields.SCHEDULED_END_TIME]

    dates_to_copy_to = DateUtils.get_dates_in_range(
        from_date_str,
        to_date_str,
        include_saturday,
        include_sunday
    )
    if not dates_to_copy_to:
        return

    employee_shifts = []

    for _dict in jobshift[JobShift.Fields.EMPLOYEE_SHIFTS]:
        employee_shift = EmployeeShift(**_dict)

        employee_shift.actual_start_time = None
        employee_shift.actual_end_time = None
        # todo ask shaheen about scheduled start and end time

        employee_shift_dict = EmployeeShift.encode(employee_shift)
        employee_shifts.append(employee_shift_dict)

    # The employees could have been assigned elsewhere, we need to remove them
    # from other jobshifts before we put them in the copied jobshifts
    employee_id_list = map(lambda x: x[EmployeeShift.Fields.EMPLOYEE_ID],
                           employee_shifts)

    dates_to_copy_to = map(lambda x: x.isoformat(), dates_to_copy_to)

    remove_employees_from_assigned_jobshifts(dates_to_copy_to, employee_id_list)

    query_dict = {
        JobShift.Fields.JOB_ID: job_id,
        JobShift.Fields.JOB_DATE: {'$in': dates_to_copy_to}
    }
    update_dict = {
        '$set': {
            JobShift.Fields.SCHEDULED_START_TIME: scheduled_start_time,
            JobShift.Fields.SCHEDULED_END_TIME: scheduled_end_time,
            JobShift.Fields.EMPLOYEE_SHIFTS: employee_shifts
        }
    }

    result = DatabaseManager.update(
        Collection.JOBSHIFTS,
        query_dict,
        update_dict,
        multi=True,
        upsert=False
    )
    # todo For now we are not doing anything with result


def remove_employees_from_assigned_jobshifts(date_list, employee_id_list):

    query_dict = {
        JobShift.Fields.JOB_DATE: {'$in': date_list}
    }
    update_dict = {
        '$pull': {
            JobShift.Fields.EMPLOYEE_SHIFTS: {
                EmployeeShift.Fields.EMPLOYEE_ID: {'$in': employee_id_list}
            }
        }
    }

    DatabaseManager.update(
        Collection.JOBSHIFTS,
        query_dict,
        update_dict,
        multi=True,
        upsert=False
    )