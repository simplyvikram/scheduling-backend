
from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import (
    schema_jobshift,
)
from scheduling_backend.database_manager import Collection, DatabaseManager
from scheduling_backend.exceptions import UserException

class JobShiftHandler(BaseHandler):

    def __init__(self):
        super(JobShiftHandler, self).__init__(schema_jobshift)

    @marshaling_handler
    def get(self, jobshift_id):

        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        return jobshift_dict

    @marshaling_handler
    def patch(self, jobshift_id):
        """
        While jobshifts are created/deleted/modified as a byproduct of
        job creation/deletion/modification, we can modify a few things
        individually just for the jobshift, like
        scheduled_start_time and scheduled_end_time
        """

        # todo implment me
        return {
            "msg": "Implement me!!!!!",
            "class": "JobShiftHandler",
            "method": "patch",
            "jobshift_id": jobshift_id
        }


    @marshaling_handler
    def post(self):
        raise UserException("Jobshifts cannot be created using apis")


    @marshaling_handler
    def delete(self):
        raise UserException("Jobshifts cannot be deleted using apis")