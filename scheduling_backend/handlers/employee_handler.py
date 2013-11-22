
from flask import current_app as current_app
from flask import request

from scheduling_backend.handlers import common_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_employee
from scheduling_backend.models import Employee


class EmployeeHandler(BaseHandler):

    def __init__(self):
        super(EmployeeHandler, self).__init__(schema_employee)


    def preprocess_data(self, data):

        if self.error:
            return

        if request.method == BaseHandler.POST:
            self._validate_post_data()
        elif request.method == BaseHandler.PATCH:
            self._validate_patch_data()


    def _validate_patch_data(self):

        if self.error:
            return

        self.validate_str_field(Employee.Fields.NAME, False)
        self.validate_str_field(Employee.Fields.CURRENT_ROLE, False)

        if self.error:
            return

        # Additional check for duplicate names
        name = self.data.get(Employee.Fields.NAME, None)
        if name is not None:
            is_name_duplicate = self._check_employee_name_in_database(name)
            if is_name_duplicate:
                self.error = {"error": "Duplicate employee name."
                                       " Choose another name"}
                return


        # Additional check to make sure current role is in the
        #     list of allowed roles
        current_role = self.data.get(Employee.Fields.CURRENT_ROLE, None)
        if current_role is not None:
            if current_role not in Employee.allowed_roles():
                self.error = {
                    "error": "Allowed values for current_role are %s" %
                             str(Employee.allowed_roles())
                }
                return


    def _validate_post_data(self):

        if self.error:
            return

        name = self.data.get(Employee.Fields.NAME, None)
        current_role = self.data.get(Employee.Fields.NAME, None)
        active = self.data.get(Employee.Fields.ACTIVE, None)

        l = [name, current_role, active]

        is_any_field_missing = BaseHandler.none_present_in_list(l)

        if is_any_field_missing:
            self.error = {"error": "Missing required field"}
            return

        self._validate_patch_data()


    def _check_employee_name_in_database(self, emp_name):

        matching_emp_count = \
            current_app.db.employees.find({Employee.Fields.NAME: emp_name}).count()

        if matching_emp_count > 0:
            return True

        return False


    @common_handler
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

    @common_handler
    def post(self):

        obj_id = current_app.db.employees.insert(self.data)
        # todo can the data have an array of employees to be inserted????
        employee = current_app.db.employees.find_one({"_id": obj_id})

        return employee


    @common_handler
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