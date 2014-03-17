from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import (
    schema_jobshift,
)
from scheduling_backend.models import JobShift, BaseModel
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

    def preprocess_PATCH(self):

        for key in self.data.keys():
            if key not in [JobShift.Fields.SCHEDULED_START_TIME,
                           JobShift.Fields.SCHEDULED_END_TIME]:
                raise UserException("Only scheduled start/end times can "
                                    "be modified for jobshifts")


    @marshaling_handler
    def patch(self, jobshift_id):
        """
        While jobshifts are created/deleted/modified as a byproduct of
        job creation/deletion/modification, we can just modify a few things
        individually just for the jobshift, like
        scheduled_start_time and scheduled_end_time
        """
        query_dict = {BaseModel.Fields._ID: jobshift_id}
        update_dict = {'$set': self.data}

        result = DatabaseManager.update(
            collection_name=Collection.JOBSHIFTS,
            query_dict=query_dict,
            update_dict=update_dict,
            multi=False,
            upsert=False
        )
        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        return jobshift_dict


    @marshaling_handler
    def post(self):
        raise UserException("Jobshifts cannot be created using apis")


    def delete(self):
        raise UserException("Jobshifts cannot be deleted using apis")