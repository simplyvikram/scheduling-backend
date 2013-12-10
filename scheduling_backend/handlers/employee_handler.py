
from flask import current_app as current_app

import flask.ext.restful.types

from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import marshaling_handler, Params
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_employee
from scheduling_backend.models import BaseModel, Employee


class EmployeeHandler(BaseHandler):

    def __init__(self):
        super(EmployeeHandler, self).__init__(schema_employee)

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.ACTIVE,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     default=None,
                                     required=False)

        self.req_parser.add_argument(Params.CURRENT_ROLE,
                                     type=str,
                                     location='args',
                                     default=None,
                                     required=False)

        self.args = self.req_parser.parse_args()



    def preprocess_PATCH(self):

        name = self.data.get(Employee.Fields.NAME, None)
        current_role = self.data.get(Employee.Fields.CURRENT_ROLE, None)

        self._validate_employee_name(name)
        self._validate_current_role(current_role)


    def preprocess_POST(self):
        self.preprocess_PATCH()


    def _validate_current_role(self, current_role):
        """
        We validate that the employee role is present is a valid one
        """

        if current_role is None:
            return
        elif current_role is '':
            raise UserException("current_role cannot be empty.")
        elif current_role not in Employee.allowed_roles():
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


    @marshaling_handler
    def get(self, obj_id=None):

        if obj_id:
            employee = current_app.db.employees.find_one(
                {BaseModel.Fields._ID: obj_id}
            )
            if employee is None:
                return {}

            return employee
        else:
            query_dict = {}

            # active is an optional param, it may or may not be present. Hence
            # we explicitly check it with True or False.
            # If absent it will be None

            active = self.args.get(Params.ACTIVE, None)
            if active is True:
                query_dict[Employee.Fields.ACTIVE] = True
            elif active is False:
                query_dict[Employee.Fields.ACTIVE] = False

            current_role = self.args.get(Params.CURRENT_ROLE, None)
            if current_role is not None:
                # It can be empty, but validate will take care of it
                self._validate_current_role(current_role)
                query_dict[Employee.Fields.CURRENT_ROLE] = current_role

            employees_cursor = current_app.db.employees.find(query_dict)
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
        employee_dict = current_app.db.employees.find_one(
            {BaseModel.Fields._ID: obj_id}
        )

        return employee_dict


    @marshaling_handler
    def patch(self, obj_id):

        _dict = self.data

        current_app.db.employees.update(
            {BaseModel.Fields._ID: obj_id}, {"$set": _dict}
        )
        employee = current_app.db.employees.find_one(
            {BaseModel.Fields._ID: obj_id}
        )
        return employee



    def delete(self, obj_id):

        result = current_app.db.employees.remove(
            {BaseModel.Fields._ID: obj_id}
        )
        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404