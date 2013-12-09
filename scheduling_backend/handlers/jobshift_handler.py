
from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import (
    schema_job_shift,
)


class JobShiftHandler(BaseHandler):

    def __init__(self):
        super(JobShiftHandler, self).__init__(schema_job_shift)

    def get(self, job_shift_id=None):
        return {"method": "GET job shift"}

    @marshaling_handler
    def post(self):
        return {"error": "Job shifts cannot be created using apis"}

    @marshaling_handler
    def delete(self):
        return {"Implement me!!!!": True}
