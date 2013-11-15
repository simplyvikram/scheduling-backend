
schema_type = "http://json-schema.org/draft-04/schema#"

from models import tag_id, Client, Employee, EmployeeShift, Job, JobShift


schema_client = {
    "$schema": schema_type,
    "title": "Client schema",
    "type": "object",
    "properties": {
        tag_id: {
            "type": "string"
        },
        Client.Tag.NAME: {
            "type": "string"
        },
        Client.Tag.ACTIVE: {
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
        tag_id: {
            "type": "string"
        },
        Employee.Tag.NAME: {
            "type": "string"
        },
        Employee.Tag.CURRENT_ROLE: {
            "type": "string"
        },
        Employee.Tag.ACTIVE: {
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
        tag_id: {
            "type": "string"
        },
        Job.Tag.CLIENT_ID: {
            "type": "string"
        },
        Job.Tag.NAME: {
            "type": "string"
        },
        Job.Tag.LOCATION: {
            "type": "string"
        },
        Job.Tag.START_DATE: {
            "type": "string",
            "format": "date"
        },
        Job.Tag.END_DATE: {
            "type": "string",
            "format": "date"
        },
        Job.Tag.SCHEDULED_START_TIME: {
            "type": "string",
            "format": "time"
        },
        Job.Tag.SCHEDULED_END_TIME: {
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

        tag_id: {
            "type": "string"
        },
        EmployeeShift.Tag.EMPLOYEE_ID: {
            "type": "string"
        },
        EmployeeShift.Tag.SCHEDULED_START_TIME: {
            "type": "string",
            "format": "time"
        },
        EmployeeShift.Tag.SCHEDULED_END_TIME: {
            "type": "string",
            "format": "time"
        },
        EmployeeShift.Tag.ACTUAL_START_TIME: {
            "type": "string",
            "format": "time"
        },
        EmployeeShift.Tag.ACTUAL_END_TIME: {
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

        tag_id: {
            "type": "string"
        },
        JobShift.Tag.JOB_ID: {
            "type": "string"
        },
        JobShift.Tag.JOB_DATE: {
            "type": "string",
            "format": "date"
        },
        JobShift.Tag.SCHEDULED_START_TIME: {
            "type": "string",
            "format": "time"
        },
        JobShift.Tag.SCHEDULED_END_TIME: {
            "type": "string",
            "format": "time"
        },
        JobShift.Tag.EMPLOYEE_SHIFTS: {
            "type": "array",
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": schema_employee_shift["properties"],
                "additionalProperties":
                    schema_employee_shift["additionalProperties"]
            }

        }
    }
}

if __name__ == "__main__":
    # todo delete this later!!!

    emp_shift1 = {
        EmployeeShift.Tag.EMPLOYEE_ID: "44",
        EmployeeShift.Tag.SCHEDULED_START_TIME: "08:00:00",
        EmployeeShift.Tag.SCHEDULED_END_TIME: "17:00:00"
    }

    emp_shift2 = {
        EmployeeShift.Tag.EMPLOYEE_ID: "33",
        EmployeeShift.Tag.SCHEDULED_START_TIME: "10:00:00",
        EmployeeShift.Tag.SCHEDULED_END_TIME: "19:00:00",

        EmployeeShift.Tag.ACTUAL_START_TIME: "08:00:00",
        EmployeeShift.Tag.ACTUAL_END_TIME: "17:00:00"


    }

    _job_shift = {
        JobShift.Tag.JOB_ID: "abc",
        JobShift.Tag.SCHEDULED_END_TIME: "08:00:00",
        JobShift.Tag.SCHEDULED_END_TIME: "18:00:00",
        JobShift.Tag.EMPLOYEE_SHIFTS: [emp_shift1, emp_shift2]
        # JobShift.Tag.employee_shifts: ["vikram", "singh"]
    }

    import jsonschema
    print "before validation----"
    jsonschema.validate(_job_shift, schema_job_shift)
    print "after validation----"