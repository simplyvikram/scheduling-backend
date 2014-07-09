from scheduling_backend.handlers import no_data_handler, marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import (
    schema_jobshift,
)
from scheduling_backend.models import JobShift, BaseModel
from scheduling_backend.utils import DateUtils
from scheduling_backend.database_manager import (
    Collection, DatabaseManager, JobOperations
)
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


class ClearJobshiftsHandler(BaseHandler):

    @no_data_handler
    def get(self, for_date_str):

        for_date_str = DateUtils.to_datetime_format(for_date_str,
                                                    DateUtils.DATE).isoformat()

        query_dict = {JobShift.Fields.JOB_DATE: for_date_str}
        jobshifts = DatabaseManager.find(
            Collection.JOBSHIFTS,
            query_dict,
            True
        )

        job_ids = map(lambda jobshift: jobshift[JobShift.Fields.JOB_ID],
                      jobshifts)
        jobshift_ids = map(lambda jobshift: jobshift[BaseModel.Fields._ID],
                           jobshifts)

        jobs = DatabaseManager.find_objects_by_ids(
            Collection.JOBS, job_ids
        )

        jobshifts_documents = []
        for job in jobs:
            jobshift = JobShift(
                job._id,
                for_date_str,
                job.scheduled_start_time,
                job.scheduled_end_time
            )
            jobshifts_documents.append(JobShift.encode(jobshift))


        # delete jobshifts for that date
        JobOperations.delete_jobshifts(jobshift_ids)

        # recreate new jobshifts for that date
        DatabaseManager.insert(Collection.JOBSHIFTS, jobshifts_documents)