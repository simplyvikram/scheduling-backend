
from flask import make_response

from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.utils import DateUtils
from scheduling_backend.models import Employee
from scheduling_backend.database_manager import (
    Collection, DatabaseManager, JobOperations
)


class HoursWorkedPerEmployeeHandler(BaseHandler):

    def __init__(self):
        super(HoursWorkedPerEmployeeHandler, self).__init__(None)


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

        jobshifts = JobOperations.find_jobshifts_for_dates(dates)

        employees_hours_worked_dict = \
            extract_aggregate_hours_worked_per_employee(jobshifts)

        all_employees = DatabaseManager.find(
            Collection.EMPLOYEES, {}, multiple=True
        )
        all_employees = map(lambda employee_dict: Employee(**employee_dict),
                            all_employees)

        lines = list()
        heading = ','.join(
            [' '] +
            map(
                lambda date_str: DateUtils.get_day_string(date_str) +
                                 ' ' +
                                 date_str,
                dates_strings
            )
        )
        lines.append(heading)

        for employee in all_employees:
            line = employee.name + '-' + str(employee._id)

            for date_string in dates_strings:

                hours_worked_dict = employees_hours_worked_dict.get(
                    employee._id, None
                )

                if hours_worked_dict:
                    # If present it indicates that this employee had an
                    # employee shift present for that date
                    hours_worked = hours_worked_dict.get(date_string, 0)
                else:
                    hours_worked = 0

                line += ',' + str(hours_worked)

            lines.append(line)

        # we now create a temporary file using result and send it back
        result = '\n'.join(lines)

        response = make_response(result)
        response.headers["Content-Disposition"] = \
            "attachment; " \
            "filename=employees_aggregate_hours_{0}_to_{1}.csv".format(
                from_date_str, to_date_str
            )
        return response


def extract_aggregate_hours_worked_per_employee(jobshifts):
    # We use a default dict to aggregate minutes worked per employee
    # That way we don't have to check if the employee id exists in the dict
    # http://blog.ludovf.net/python-collections-defaultdict/
    from collections import defaultdict
    # minutes_worked_per_employee = defaultdict(int)

    # A dictionary of employees id and a dictionary representing the hours
    # worked on each of the dates
    employee_hours_worked_dict = defaultdict(dict)

    for jobshift in jobshifts:

        job_date = jobshift.job_date

        employee_shifts = jobshift.employee_shifts
        for employee_shift in employee_shifts:

            # todo run the formula through Shaheen
            start_time = employee_shift.actual_start_time
            if not start_time:
                start_time = employee_shift.scheduled_start_time
            if not start_time:
                start_time = jobshift.scheduled_start_time

            # todo run the formula through Shaheen
            end_time = employee_shift.actual_end_time
            if not end_time:
                end_time = employee_shift.scheduled_end_time
            if not end_time:
                end_time = jobshift.scheduled_end_time

            start_time = DateUtils.get_datetime_from_time(start_time)
            end_time = DateUtils.get_datetime_from_time(end_time)

            # We will return hours worked as float or int
            hours_worked = (end_time - start_time).total_seconds() / 3600
            hours_worked = round(hours_worked, 2)
            if hours_worked.is_integer():
                hours_worked = int(hours_worked)

            employee_id = employee_shift.employee_id

            # Since its a dictionary of employee ids to a dictionary
            employee_hours_worked_dict[employee_id][job_date] = hours_worked

    return employee_hours_worked_dict