
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

class Equipment(BaseModel):

    class Fields(object):
        NAME = "name"
        TYPE = "type"

    def __init__(self, name, type, _id=None):
        super(Equipment, self).__init__(_id)

        self.name = name
        self.type = type

    @classmethod
    def encode(cls, equipment):
        d = {
            Equipment.Fields.NAME: equipment.name,
            Equipment.Fields.TYPE: equipment.type
        }
        if equipment._id:
            d[BaseModel.Fields._ID] = equipment._id

        return d

    def __repr__(self):

        _ = "<Employee name:{name}, type:{type}, _id:{_id}>"
        _ = _.format(name=self.name, type=self.type, _id=self._id)
        return _

    @classmethod
    def allowed_types(cls):
        return ["fork lift", "bulldozer", "shovel", "hammer"]


class Job(BaseModel):

    class Fields(object):
        CLIENT_ID = "client_id"
        NAME = "name"
        LOCATION = "location"
        TIME_AND_MATERIAL = "time_and_material"

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
                 client_id, name, location, time_and_material,
                 start_date,
                 end_date,
                 scheduled_start_time,
                 scheduled_end_time,
                 _id=None):

        super(Job, self).__init__(_id)
        self.client_id = client_id
        self.name = name
        self.location = location
        self.time_and_material = time_and_material

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
            Job.Fields.TIME_AND_MATERIAL: job.time_and_material,

            Job.Fields.START_DATE: job.start_date,
            Job.Fields.END_DATE: job.end_date,

            Job.Fields.SCHEDULED_START_TIME: job.scheduled_start_time,
            Job.Fields.SCHEDULED_END_TIME: job.scheduled_end_time
        }
        if job._id:
            d[BaseModel.Fields._ID] = job._id

        return d


class EmployeeShift(object):
    # caution we inherit this from object instead of BaseModel as this is
    # included as part of jobshift and does not need an _id
    class Fields(object):

        EMPLOYEE_ID = "employee_id"
        SHIFT_ROLE = "shift_role"

        SCHEDULED_START_TIME = "scheduled_start_time"
        SCHEDULED_END_TIME = "scheduled_end_time"
        ACTUAL_START_TIME = "actual_start_time"
        ACTUAL_END_TIME = "actual_end_time"

    def __init__(self, employee_id,
                 shift_role,
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
        self.shift_role = shift_role

        self.scheduled_start_time = scheduled_start_time
        self.scheduled_end_time = scheduled_end_time
        self.actual_start_time = actual_start_time
        self.actual_end_time = actual_end_time


    @classmethod
    def encode(cls, employeeshift):
        d = {
            EmployeeShift.Fields.EMPLOYEE_ID: employeeshift.employee_id,

            EmployeeShift.Fields.SHIFT_ROLE: employeeshift.shift_role,

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

class EquipmentShift(object):

    class Fields(object):
        EQUIPMENT_ID = "equipment_id"

    def __init__(self, equipment_id):
        super(EquipmentShift, self).__init__()

        self.equipment_id = equipment_id

    @classmethod
    def encode(cls, equipment_shift):
        d = {
            EquipmentShift.Fields.EQUIPMENT_ID: equipment_shift.equipment_id
        }

        return d


class JobShift(BaseModel):

    class Fields(object):
        JOB_ID = "job_id"
        JOB_DATE = "job_date"

        SCHEDULED_START_TIME = "scheduled_start_time"
        SCHEDULED_END_TIME = "scheduled_end_time"

        EMPLOYEE_SHIFTS = "employee_shifts"
        EQUIPMENT_SHIFTS = "equipment_shifts"

    def __init__(self, job_id, job_date,
                 scheduled_start_time,
                 scheduled_end_time,
                 employee_shifts=list(),
                 equipment_shifts=list(),
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

        # We dont have a scenario now where this can happen,
        # but putting this for safety. If either employee_shifts or
        # equipment_shifts is None
        if employee_shifts is None:
            self.employee_shifts = list()
        if equipment_shifts is None:
            self.equipment_shifts = list()

        self.employee_shifts = map(
            lambda _dict: EmployeeShift(**_dict),
            employee_shifts
        )
        self.equipment_shifts = map(
            lambda _dict: EquipmentShift(**_dict),
            equipment_shifts
        )


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

        # This may never happen as we take of this in jobshift,
        # but just being sure
        if job_shift.employee_shifts is None:
            job_shift.employee_shifts = list()
        if job_shift.equipment_shifts is None:
            job_shift.equipment_shifts = list()

        employee_shifts = map(lambda x: EmployeeShift.encode(x),
                              job_shift.employee_shifts)
        d[JobShift.Fields.EMPLOYEE_SHIFTS] = employee_shifts

        equipment_shifts = map(lambda x: EquipmentShift.encode(x),
                               job_shift.equipment_shifts)
        d[JobShift.Fields.EQUIPMENT_SHIFTS] = equipment_shifts

        return d

    def contains_employee(self, employee_id):

        _ = filter(lambda x: x.employee_id == employee_id,
                   self.employee_shifts)

        return bool(len(list(_)))

    def contains_equipment(self, equipment_id):

        _ = filter(lambda x: x.equipment_id == equipment_id,
                   self.equipment_shifts)

        return bool(len(list(_)))