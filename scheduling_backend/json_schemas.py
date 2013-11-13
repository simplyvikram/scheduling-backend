
schema_type = "http://json-schema.org/draft-04/schema#"

from models import tag_id, Client, Job, Employee


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