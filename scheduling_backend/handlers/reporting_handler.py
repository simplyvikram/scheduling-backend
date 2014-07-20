
from itertools import groupby
from collections import defaultdict

from flask import make_response

from scheduling_backend.handlers import (
    authentication_handler,
    Params,
    no_data_handler
)
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.utils import DateUtils
from scheduling_backend.models import Employee
from scheduling_backend.database_manager import (
    Collection, DatabaseManager, JobOperations
)


class HoursWorkedPerEmployeeHandler(BaseHandler):

    def __init__(self):
        super(HoursWorkedPerEmployeeHandler, self).__init__(None)

    @authentication_handler
    def get(self, from_date_str, to_date_str):

        from_date_str = DateUtils.to_datetime_format(from_date_str,
                                                     DateUtils.DATE).isoformat()

        to_date_str = DateUtils.to_datetime_format(to_date_str,
                                                   DateUtils.DATE).isoformat()

        self.validate_start_and_end_dates(from_date_str, to_date_str)

        dates = DateUtils.get_dates_in_range(
            from_date_str, to_date_str,
            include_saturday=True, include_sunday=True
        )
        dates_strings = map(lambda date: date.isoformat(), dates)

        jobshifts = JobOperations.find_jobshifts(dates_strings=dates_strings)

        employees_hours_worked_dict = \
            extract_aggregate_hours_worked_per_employee(jobshifts)

        all_employees = DatabaseManager.find(
            Collection.EMPLOYEES, {}, multiple=True
        )
        all_employees = map(lambda employee_dict: Employee(**employee_dict),
                            all_employees)

        lines = list()

        heading = extract_dates_heading_line(dates_strings)
        heading = heading.split(',')
        heading.append('Total hours worked')
        heading.append('Weekday earnings')
        heading.append('Weekend earnings')
        heading.append('Total earnings')
        heading = ','.join(heading)

        lines.append(heading)

        for employee in all_employees:
            # line = employee.name + '-' + str(employee._id)
            line = employee.name

            hours_worked_dict = employees_hours_worked_dict.get(employee._id,
                                                                None)
            # hours_worked_dict may be absent for that employee_id, indicating
            # that that employee did not work on any of the given dates

            weekday_hours_worked = 0
            weekend_hours_worked = 0
            for date_str in dates_strings:

                hours_worked = 0
                if hours_worked_dict:
                    hours_worked = hours_worked_dict.get(date_str, 0)

                    if DateUtils.is_weekday(date_str):
                        weekday_hours_worked += hours_worked
                    else:
                        weekend_hours_worked += hours_worked

                line += ',' + str(hours_worked)

            weekday_earnings = round(
                float(weekday_hours_worked * employee.weekday_rate), 2
            )
            weekend_earnings = round(
                float(weekend_hours_worked * employee.weekend_rate), 2
            )
            line += ',' + str(weekday_hours_worked + weekend_hours_worked)
            line += ',' + str(weekday_earnings)
            line += ',' + str(weekend_earnings)
            line += ',' + str(weekday_earnings + weekend_earnings)
            lines.append(line)

        # we now create a temporary file using result and send it back
        file_content = '\n'.join(lines)

        file_name = "employees_hours_{0}_to_{1}.csv"
        file_name = file_name.format(
            from_date_str, to_date_str
        )
        response = generate_file_response(file_content, file_name)
        return response

class HoursWorkedPerShiftRole(BaseHandler):

    def __init__(self):
        super(HoursWorkedPerShiftRole, self).__init__(None)

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.FROM_DATE,
                                     type=str,
                                     location='args',
                                     required=False,
                                     default=None)

        self.req_parser.add_argument(Params.TO_DATE,
                                     type=str,
                                     location='args',
                                     required=False,
                                     default=None)

        self.args = self.req_parser.parse_args()


    @authentication_handler
    def get(self, job_id):

        job = DatabaseManager.find_object_by_id(Collection.JOBS, job_id, True)

        from_date_str = self.args.get(Params.FROM_DATE, None)
        if not from_date_str:
            from_date_str = job.start_date
        from_date_str = DateUtils.to_datetime_format(from_date_str,
                                                     DateUtils.DATE).isoformat()

        to_date_str = self.args.get(Params.TO_DATE, None)
        if not to_date_str:
            to_date_str = job.end_date
        to_date_str = DateUtils.to_datetime_format(to_date_str,
                                                   DateUtils.DATE).isoformat()

        self.validate_start_and_end_dates(from_date_str, to_date_str)
        dates = DateUtils.get_dates_in_range(
            from_date_str, to_date_str,
            include_saturday=True, include_sunday=True
        )
        dates_strings = map(lambda x: x.isoformat(), dates)

        jobshifts = JobOperations.find_jobshifts(dates_strings=dates_strings,
                                                 job_id=job_id)
        shift_role_hours_worked_dict = \
            extract_aggregate_hours_worked_per_role(jobshifts)

        all_shift_roles = Employee.allowed_roles()

        lines = list()
        heading = extract_dates_heading_line(dates_strings)

        heading = heading.split(',')
        heading.append('Total hours worked')
        heading = ','.join(heading)

        lines.append(heading)

        for role in all_shift_roles:
            line = role

            hours_worked_dict = shift_role_hours_worked_dict.get(role, None)
            # hours_worked_dict may be absent for that role, indicating
            # that no employee with the given role, worked on any of the
            # given dates

            total_hours_worked = 0
            for date_str in dates_strings:

                hours_worked = 0
                if hours_worked_dict:
                    hours_worked = hours_worked_dict.get(date_str, 0)
                    total_hours_worked += hours_worked

                line += ',' + str(hours_worked)

            line += ',' + str(total_hours_worked)
            lines.append(line)

        file_content = '\n'.join(lines)
        file_name = "shift_role_hours_" \
                    "job_{job_id}_{job_name}_{from_date}_to_{to_date}.csv"
        file_name = file_name.format(
            job_id=job_id, job_name=job.name,
            from_date=from_date_str, to_date=to_date_str
        )

        response = generate_file_response(file_content, file_name)
        return response


def extract_dates_heading_line(dates_strings):

    # line = map(lambda date_str: DateUtils.get_day_string(date_str) +
    #                             ' ' +
    #                             date_str,
    #            dates_strings)

    line = list(dates_strings)

    line.insert(0, '')

    line = ','.join(line)

    return line


def generate_file_response(file_content, complete_file_name):

    content_key = "Content-Disposition"
    content_value = "attachment; filename={0}".format(complete_file_name)

    response = make_response(file_content)
    response.headers[content_key] = content_value
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def extract_aggregate_hours_worked_per_role(jobshifts):
    """
    Returns a defaultdict of shift_role to a dict containing the following
    information:
    {
        "shift_role1": {
            "date_string1": "hours_worked1",
            "date_string2": "hours_worked2"
        }
    }
    """
    _dict = defaultdict(dict)
    for jobshift in jobshifts:

        job_date = jobshift.job_date

        def _calc_hours_worked(employee_shift):
            return hours_an_employee_worked_in_shift(employee_shift, jobshift)

        employee_shifts = sorted(jobshift.employee_shifts,
                                 key=lambda x: x.shift_role)

        for role, grouped_employee_shifts in groupby(employee_shifts,
                                                     lambda x: x.shift_role):

            grouped_employee_shifts = list(grouped_employee_shifts)

            hours_worked_list = map(lambda x: _calc_hours_worked(x),
                                    grouped_employee_shifts)

            _dict[role][job_date] = sum(hours_worked_list)

    return _dict


def extract_aggregate_hours_worked_per_employee(jobshifts):
    """
    Returns a defaultdict of employee ids to a dict containing the following
    information:
    {
        "employee_id_1": {
            "date_string1": "hours_worked1
            "date_string2: "hours_worked2
        },
    }
    """
    # We use a default dict to aggregate minutes worked per employee
    # That way we don't have to check if the employee id exists in the dict
    # http://blog.ludovf.net/python-collections-defaultdict/
    # minutes_worked_per_employee = defaultdict(int)

    # A dictionary of employees id and a dictionary representing the hours
    # worked on each of the dates

    _dict = defaultdict(dict)
    for jobshift in jobshifts:

        job_date = jobshift.job_date

        for employee_shift in jobshift.employee_shifts:

            employee_id = employee_shift.employee_id
            hours_worked = hours_an_employee_worked_in_shift(
                employee_shift, jobshift
            )

            # Since its a dictionary of employee ids to a dictionary
            _dict[employee_id][job_date] = hours_worked

    return _dict

def minutes_an_employee_worked_in_shift(employee_shift, jobshift):
    """
    Returns the minutes worked as an int

    """
    # todo run the formula through Shaheen
    # caution Don't forget!

    start_time = employee_shift.actual_start_time
    if not start_time:
        start_time = employee_shift.scheduled_start_time
    if not start_time:
        start_time = jobshift.scheduled_start_time

    end_time = employee_shift.actual_end_time
    if not end_time:
        end_time = employee_shift.scheduled_end_time
    if not end_time:
        end_time = jobshift.scheduled_end_time

    start_time = DateUtils.get_datetime_from_time(start_time)
    end_time = DateUtils.get_datetime_from_time(end_time)

    # We will return hours worked as float or int
    minutes_worked = (end_time - start_time).total_seconds() / 60
    return int(minutes_worked)


def hours_an_employee_worked_in_shift(employee_shift, jobshift):
    """
    Returns the hours worked as an int or float
    """
    # todo run the formula through Shaheen
    # caution Don't forget!
    minutes_worked = minutes_an_employee_worked_in_shift(employee_shift,
                                                         jobshift)

    hours_worked = minutes_worked / 60.0
    hours_worked = round(hours_worked, 2)
    if hours_worked.is_integer():
        hours_worked = int(hours_worked)

    return hours_worked
