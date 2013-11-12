
schema_type = "http://json-schema.org/draft-04/schema#"

schema_client = {
    "$schema": schema_type,
    "title": "Client schema",
    "type": "object",
    "properties": {
        "_id": {
            "type": "string"
        },
        "name": {
            "type": "string"
        },
        "active": {
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
        "_id": {
          "type": "string"
        },
        "client_id": {
            "type": "string"
        },
        "client_name": {
          "type": "string"
        },
        "location": {
            "type": "string"
        },
        "start_date": {
            "type": "string",
            "format": "date"
        },
        "end_date": {
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
        "_id": {
          "type": "string"
        },
        "current_role": {
            "type": "string"
        },
        "active": {
          "type": "boolean"
        },
    },
    "additionalProperties": False
}