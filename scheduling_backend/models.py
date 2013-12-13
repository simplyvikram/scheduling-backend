
class BaseModel(object):

    class Fields(object):
        _ID = "_id"

    def __init__(self, _id):
        super(BaseModel, self).__init__()
        self._id = _id

class Client(BaseModel):

    class Fields(object):
        NAME = "name"
        ACTIVE = "active"

    def __init__(self, name, active, _id=None):

        super(Client, self).__init__(_id)

        self.name = name
        self.active = active



    @classmethod
    def encode(cls, client):
        d = {
            Client.Fields.NAME: client.name,
            Client.Fields.ACTIVE: client.active
        }
        if client._id:
            d[BaseModel.Fields._ID] = client._id

        return d


class Employee(BaseModel):

    class Fields(object):
        NAME = "name"
        CURRENT_ROLE = "current_role"
        ACTIVE = "active"

    def __init__(self, name, current_role, active, _id=None):
        super(Employee, self).__init__(_id)

        self.name = name
        self.current_role = current_role
        self.active = active


    @classmethod
    def encode(cls, employee):
        d = {
            Employee.Fields.NAME: employee.name,
            Employee.Fields.CURRENT_ROLE: employee.current_role,
            Employee.Fields.ACTIVE: employee.active
        }
        if employee._id:
            d[BaseModel.Fields._ID] = employee._id

        return d


    @classmethod
    def allowed_roles(cls):
        return ['plumber', 'worker', 'carpenter',
                'fitter', 'slacker']

    def __repr__(self):
        return "<Employee %s:%s %s:%s, %s:%s, %s:%s>" % \
               (BaseModel.Fields._ID, str(self._id),
                Employee.Fields.NAME, self.name,
                Employee.Fields.CURRENT_ROLE, self.current_role,
                Employee.Fields.ACTIVE, str(self.active))

class Job(BaseModel):

    class Fields(object):
        CLIENT_ID = "client_id"
        NAME = "name"
        LOCATION = "location"

        START_DATE = "start_date"
        END_DATE = "end_date"

        SCHEDULED_START_TIME = "scheduled_start_time"
        SCHEDULED_END_TIME = "scheduled_end_time"

    # todo currently these are required
    # DEFAULT_START_TIME = datetime.time(hour=8, minute=0, second=0)
    # DEFAULT_END_TIME = datetime.time(hour=16, minute=0, second=0)
    # DEFAULT_START_TIME = "08:00:00"
    # DEFAULT_END_TIME = "05:00:00"

    def __init__(self,
                 client_id, name, location,
                 start_date,
                 end_date,
                 scheduled_start_time,
                 scheduled_end_time,
                 _id=None):

        super(Job, self).__init__(_id)
        self.client_id = client_id
        self.name = name
        self.location = location

        self.start_date = start_date
        self.end_date = end_date

        self.scheduled_start_time = scheduled_start_time
        self.scheduled_end_time = scheduled_end_time


    @classmethod
    def encode(cls, job):
        d = {
            Job.Fields.CLIENT_ID: job.client_id,
            Job.Fields.NAME: job.name,
            Job.Fields.LOCATION: job.location,

            Job.Fields.START_DATE: job.start_date,
            Job.Fields.END_DATE: job.end_date,

            Job.Fields.SCHEDULED_START_TIME: job.scheduled_start_time,
            Job.Fields.SCHEDULED_END_TIME: job.scheduled_end_time
        }
        if job._id:
            d[BaseModel.Fields._ID] = job._id

        return d


class EmployeeShift(object):
    # caution we inherit this from model instead of object as this is
    # included as part of jobshift and does not need an _id
    class Fields(object):

        EMPLOYEE_ID = "employee_id"

        SCHEDULED_START_TIME = "scheduled_start_time"
        SCHEDULED_END_TIME = "scheduled_end_time"

        ACTUAL_START_TIME = "actual_start_time"
        ACTUAL_END_TIME = "actual_end_time"

    def __init__(self, employee_id,
                 scheduled_start_time,
                 scheduled_end_time,
                 actual_start_time=None,
                 actual_end_time=None):
        """
        Use actual start/end times for all calculations. If they are
        absent use the scheduled start/end times for the calculations.
        """

        super(EmployeeShift, self).__init__()
        # todo ask shaheen about above
        self.employee_id = employee_id

        self.scheduled_start_time = scheduled_start_time
        self.scheduled_end_time = scheduled_end_time
        self.actual_start_time = actual_start_time
        self.actual_end_time = actual_end_time


    @classmethod
    def encode(cls, employeeshift):
        d = {
            EmployeeShift.Fields.EMPLOYEE_ID: employeeshift.employee_id,

            EmployeeShift.Fields.SCHEDULED_START_TIME:
                employeeshift.scheduled_start_time,

            EmployeeShift.Fields.SCHEDULED_END_TIME:
                employeeshift.scheduled_end_time,

            EmployeeShift.Fields.ACTUAL_START_TIME:
                employeeshift.actual_start_time,

            EmployeeShift.Fields.ACTUAL_END_TIME:
                employeeshift.actual_end_time
        }

        return d


class JobShift(BaseModel):

    class Fields(object):
        JOB_ID = "job_id"
        JOB_DATE = "job_date"

        SCHEDULED_START_TIME = "scheduled_start_time"
        SCHEDULED_END_TIME = "scheduled_end_time"

        EMPLOYEE_SHIFTS = "employee_shifts"

    def __init__(self, job_id, job_date,
                 scheduled_start_time,
                 scheduled_end_time,
                 employee_shifts=list(),
                 _id=None):
        """
        Always need to specify scheduled_start_time. When we create job_shifts
        initally they either from the copied job shift, or from the current
        initally they either from the copied job shift, or from the current
        values in the job
        """
        super(JobShift, self).__init__(_id)

        self.job_id = job_id
        self.job_date = job_date

        self.scheduled_start_time = scheduled_start_time
        self.scheduled_end_time = scheduled_end_time

        self.employee_shifts = employee_shifts


    @classmethod
    def encode(cls, job_shift):
        d = {
            JobShift.Fields.JOB_ID: job_shift.job_id,
            JobShift.Fields.JOB_DATE: job_shift.job_date,

            JobShift.Fields.SCHEDULED_START_TIME: job_shift.scheduled_start_time,
            JobShift.Fields.SCHEDULED_END_TIME: job_shift.scheduled_end_time
        }
        if job_shift._id:
            d[BaseModel.Fields._ID] = job_shift._id

        if not job_shift.employee_shifts:
            # If employee_shifts is none or empty
            job_shift.employee_shifts = []


        _list = map(lambda emp_shift: EmployeeShift.encode(emp_shift),
                    job_shift.employee_shifts)

        d[JobShift.Fields.EMPLOYEE_SHIFTS] = _list

        return d