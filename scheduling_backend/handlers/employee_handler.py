
from flask import current_app as current_app

from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_employee
from scheduling_backend.models import Employee


class EmployeeHandler(BaseHandler):

    def __init__(self):
        super(EmployeeHandler, self).__init__(schema_employee)


    def preprocess_PATCH(self):

        name = self.data.get(Employee.Fields.NAME, None)
        current_role = self.data.get(Employee.Fields.CURRENT_ROLE, None)

        self._validate_employee_name(name)
        self._validate_employee_role(current_role)


    def preprocess_POST(self):
        self.preprocess_PATCH()


    def _validate_employee_role(self, current_role):
        """
        We validate that the employee role is present is a valid one
        """
        current_role_present = isinstance(current_role, str)
        if current_role_present:
            if current_role not in Employee.allowed_roles():
                raise UserException("Allowed values for current_role are %s" %
                                    str(Employee.allowed_roles()))


    def _validate_employee_name(self, emp_name):
        """
        We check if the employee name, if present is a valid one
        """
        if emp_name == '':
            raise UserException("Employeee name cannot be empty")

        matching_emp_count = current_app.db.employees.find(
            {Employee.Fields.NAME: emp_name}
        ).count()

        if matching_emp_count > 0:
            raise UserException("Duplicate employee name, choose another name")


    def get(self, obj_id=None):

        if obj_id:
            employee = current_app.db.employees.find_one({"_id": obj_id})
            if employee is None:
                return {}

            return employee
        else:
            employees_cursor = current_app.db.employees.find()
            employee_list = list(employees_cursor)

            return employee_list

    @marshaling_handler
    def post(self):
        # We do this, to make sure, we have all the data we need to create
        # the employee, if not an exception is raised
        temp = Employee(**self.data)
        employee_dict = Employee.encode(temp)

        obj_id = current_app.db.employees.insert(employee_dict)
        # todo can the data have an array of employees to be inserted????
        employee_dict = current_app.db.employees.find_one({"_id": obj_id})

        return employee_dict


    @marshaling_handler
    def patch(self, obj_id):

        _dict = self.data

        current_app.db.employees.update({"_id": obj_id}, {"$set": _dict})
        employee = current_app.db.employees.find_one({"_id": obj_id})
        return employee



    def delete(self, obj_id):

        result = current_app.db.employees.remove({"_id": obj_id})
        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404