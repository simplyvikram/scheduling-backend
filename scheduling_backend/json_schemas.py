
schema_type = "http://json-schema.org/draft-04/schema#"

from models import field_id, Client, Employee, EmployeeShift, Job, JobShift


schema_client = {
    "$schema": schema_type,
    "title": "Client schema",
    "type": "object",
    "properties": {
        field_id: {
            "type": "string"
        },
        Client.Fields.NAME: {
            "type": "string"
        },
        Client.Fields.ACTIVE: {
            "type": "boolean"
        }
    },
    "additionalProperties": False
}


schema_employee = {
    "$schema": schema_type,
    "title": "Employee schema",
    "type": "object",
    "properties": {
        field_id: {
            "type": "string"
        },
        Employee.Fields.NAME: {
            "type": "string"
        },
        Employee.Fields.CURRENT_ROLE: {
            "type": "string"
        },
        Employee.Fields.ACTIVE: {
            "type": "boolean"
        },
    },
    "additionalProperties": False
}


schema_job = {
    "$schema": schema_type,
    "title": "Job schema",
    "type": "object",
    "properties": {

        field_id: {
            "type": "string"
        },
        Job.Fields.CLIENT_ID: {
            "type": "string"
        },
        Job.Fields.NAME: {
            "type": "string"
        },
        Job.Fields.LOCATION: {
            "type": "string"
        },
        Job.Fields.START_DATE: {
            "type": "string",
            "format": "date"
        },
        Job.Fields.END_DATE: {
            "type": "string",
            "format": "date"
        },
        Job.Fields.SCHEDULED_START_TIME: {
            "type": "string",
            "format": "time"
        },
        Job.Fields.SCHEDULED_END_TIME: {
            "type": "string",
            "format": "time"
        }
    },
    "additionalProperties": False
}


schema_employee_shift = {
    "$schema": schema_type,
    "title": "Employee shift schema",
    "type": "object",
    "properties": {

        field_id: {
            "type": "string"
        },
        EmployeeShift.Fields.EMPLOYEE_ID: {
            "type": "string"
        },
        EmployeeShift.Fields.SCHEDULED_START_TIME: {
            "type": "string",
            "format": "time"
        },
        EmployeeShift.Fields.SCHEDULED_END_TIME: {
            "type": "string",
            "format": "time"
        },
        EmployeeShift.Fields.ACTUAL_START_TIME: {
            "type": "string",
            "format": "time"
        },
        EmployeeShift.Fields.ACTUAL_END_TIME: {
            "type": "string",
            "format": "time"
        }
    },
    "additionalProperties": False
}

schema_job_shift = {
    "$schema": schema_type,
    "title": "Employee shift schema",
    "type": "object",
    "properties": {

        field_id: {
            "type": "string"
        },
        JobShift.Fields.JOB_ID: {
            "type": "string"
        },
        JobShift.Fields.JOB_DATE: {
            "type": "string",
            "format": "date"
        },
        JobShift.Fields.SCHEDULED_START_TIME: {
            "type": "string",
            "format": "time"
        },
        JobShift.Fields.SCHEDULED_END_TIME: {
            "type": "string",
            "format": "time"
        },
        JobShift.Fields.EMPLOYEE_SHIFTS: {
            "type": "array",
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": schema_employee_shift["properties"],
                "additionalProperties":
                    schema_employee_shift["additionalProperties"]
            }

        }
    },
    "additionalProperties": False
}

if __name__ == "__main__":
    # todo delete this later!!!

    emp_shift1 = {
        EmployeeShift.Fields.EMPLOYEE_ID: "44",
        EmployeeShift.Fields.SCHEDULED_START_TIME: "08:00:00",
        EmployeeShift.Fields.SCHEDULED_END_TIME: "17:00:00"
    }

    emp_shift2 = {
        EmployeeShift.Fields.EMPLOYEE_ID: "33",
        EmployeeShift.Fields.SCHEDULED_START_TIME: "10:00:00",
        EmployeeShift.Fields.SCHEDULED_END_TIME: "19:00:00",

        EmployeeShift.Fields.ACTUAL_START_TIME: "08:00:00",
        EmployeeShift.Fields.ACTUAL_END_TIME: "17:00:00"
    }

    _job_shift = {
        JobShift.Fields.JOB_ID: "abc",
        JobShift.Fields.SCHEDULED_END_TIME: "08:00:00",
        JobShift.Fields.SCHEDULED_END_TIME: "18:00:00",

        JobShift.Fields.EMPLOYEE_SHIFTS: [emp_shift1, emp_shift2]
        # JobShift.Fields.EMPLOYEE_SHIFTS: ["vikram", "singh"]
    }

    import jsonschema
    print "before validation----"
    jsonschema.validate(_job_shift, schema_job_shift)
    print "after validation----"