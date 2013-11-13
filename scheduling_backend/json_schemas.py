
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
        Client.tag_name: {
            "type": "string"
        },
        Client.tag_active: {
            "type": "boolean"
        }
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
        Job.tag_client_id: {
            "type": "string"
        },
        Job.tag_name: {
            "type": "string"
        },
        Job.tag_location: {
            "type": "string"
        },
        Job.tag_start_date: {
            "type": "string",
            "format": "date"
        },
        Job.tag_end_date: {
            "type": "string",
            "format": "date"
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
        Employee.tag_name: {
            "type": "string"
        },
        Employee.tag_current_role: {
            "type": "string"
        },
        Employee.tag_active: {
            "type": "boolean"
        },
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
        EmployeeShift.tag_employee_id: {
            "type": "string"
        },
        EmployeeShift.tag_actual_start_time: {
            "type": "string",
            "format": "time"
        },
        EmployeeShift.tag_actual_end_time: {
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
        JobShift.tag_job_id: {
            "type": "string"
        },
        JobShift.tag_job_date: {
            "type": "string",
            "format": "date"
        },
        JobShift.tag_scheduled_start_time: {
            "type": "string",
            "format": "time"
        },
        JobShift.tag_scheduled_end_time: {
            "type": "string",
            "format": "time"
        },
        JobShift.tag_employee_shifts: {
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
    emp_shift1 = {
        EmployeeShift.tag_employee_id: "44",
        EmployeeShift.tag_actual_start_time: "08:00:00",
        EmployeeShift.tag_actual_end_time: "17:00:00"
    }

    emp_shift2 = {
        EmployeeShift.tag_employee_id: "33",
        EmployeeShift.tag_actual_start_time: "10:00:00",
        EmployeeShift.tag_actual_end_time: "19:00:00"
    }

    _job_shift = {
        JobShift.tag_job_id: "abc",
        JobShift.tag_scheduled_end_time: "08:00:00",
        JobShift.tag_scheduled_end_time: "18:00:00",
        JobShift.tag_employee_shifts: [emp_shift1, emp_shift2]
        # JobShift.tag_employee_shifts: ["vikram", "singh"]
    }

    import jsonschema
    print "before validation----"
    jsonschema.validate(_job_shift, schema_job_shift)
    print "after validation----"