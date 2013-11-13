
from flask import current_app as current_app
from flask import request

from scheduling_backend.handlers import object_id_handler
from scheduling_backend.handlers.base_handler import BaseHandler

from scheduling_backend.json_schemas import schema_employee

from scheduling_backend.models import Employee

class EmployeeHandler(BaseHandler):

    def __init__(self):
        super(EmployeeHandler, self).__init__(schema_employee)

    def preprocess_data(self, data):
        if request.method == "POST":

            self._check_name_field_present()
            if self.error:
                return

            self._check_name_not_empty()
            if self.error:
                return

            emp_name = self._extract_employee_name_from_data()
            self._check_name_not_duplicate(emp_name)
            if self.error:
                return

    def _check_name_field_present(self):
        """
        Returns an error if name field is absent in self.data
        """
        emp_name = self.data.get(Employee.tag_name, None)
        if not emp_name:
            self.error = {"error": "Employee name field needs to be present"}

    def _check_name_not_empty(self):
        """
        Returns an error if self.data contains an empty name field
        """
        emp_name = self.data.get(Employee.tag_name, '')
        if emp_name == '':
            self.error = {"error": "Employee cannot have an empty name"}

    def _check_name_not_duplicate(self, emp_name):
        """
        Returns an error if there is an employee with the same name exists
        """
        matching_emp_count = \
            current_app.db.employees.find({Employee.tag_name: emp_name}).count()
        print "matching emp count", matching_emp_count
        if matching_emp_count > 0:
            self.error = {
                "error": "Cannot have two employees with the same name"
            }

    def _extract_employee_name_from_data(self):
        emp_name = self.data.get(Employee.tag_name, '')
        return emp_name.strip()



    @object_id_handler
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

    @object_id_handler
    def post(self):

        obj_id = current_app.db.employees.insert(self.data)
        # todo can the data have an array of employees to be inserted????
        employee = current_app.db.employees.find_one({"_id": obj_id})

        return employee


    @object_id_handler
    def patch(self, obj_id):

        current_app.db.employees.update({"_id": obj_id}, {"$set": self.data})
        employee = current_app.db.employees.find_one({"_id": obj_id})
        return employee


    def delete(self, obj_id):

        result = current_app.db.employees.remove({"_id": obj_id})
        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404