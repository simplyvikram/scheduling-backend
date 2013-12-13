
from flask import current_app
from models import BaseModel, Job, Employee, Client, EmployeeShift, JobShift
from exceptions import UserException

class Collection(object):
    EMPLOYEES = 'employees'
    CLIENTS = 'clients'
    JOBS = 'jobs'
    JOBSHIFTS = 'jobshifts'

class DatabaseManager(object):

    @staticmethod
    def find(collection_name, query_dict={}, multiple=False):

        if multiple:
            docs = current_app.db[collection_name].find(query_dict)
            return list(docs)
        else:
            doc = current_app.db[collection_name].find_one(query_dict)
            return doc


    @staticmethod
    def update(collection_name,
               query_dict, update_dict,
               multi=True, upsert=False):


        print "Inside update query_dict:", query_dict
        print "Inside update update_dict:", update_dict
        print "Inside update collection name", collection_name
        result = current_app.db[collection_name].update(
            query_dict,
            update_dict,
            multi=multi,
            upsert=upsert
        )
        return result

    @staticmethod
    def remove(collection_name,
               query_dict, multiple=False):

        justOne = True
        if multiple:
            justOne = False

        result = current_app.db[collection_name]. remove(
            query_dict, justOne=justOne
        )
        return result


    @staticmethod
    def find_document_by_id(collection_name, _id, exception_if_not_found=False):

        document = DatabaseManager.find(
            collection_name,
            {BaseModel.Fields._ID: _id},
            multiple=False
        )

        if not document and exception_if_not_found:
            msg = "No %s exist with _id:%s" % (collection_name, str(_id))
            raise UserException(msg)

        return document

    @staticmethod
    def find_object_by_id(collection_name, _id, exception_if_not_found=False):

        document = DatabaseManager.find_document_by_id(collection_name,
                                                       _id,
                                                       exception_if_not_found)
        if not document:
            return

        _dict = {
            Collection.CLIENTS: Client,
            Collection.JOBSHIFTS: JobShift,
            Collection.EMPLOYEES: Employee,
            Collection.JOBS: Job
        }

        return _dict[collection_name](**document)


class JobOperations(object):

    @staticmethod
    def find_jobshift_by_date_and_employee_id(employee_id, job_date):

        query = {
            JobShift.Fields.JOB_DATE: job_date,
            JobShift.Fields.EMPLOYEE_SHIFTS: {
                '$elemMatch': {EmployeeShift.Fields.EMPLOYEE_ID: employee_id}
            }
        }

        jobshift_dict = DatabaseManager.find(
            Collection.JOBSHIFTS, query, False
        )
        if jobshift_dict:
            return JobShift(**jobshift_dict)


    @staticmethod
    def find_jobshift_by_id_and_employee_id(_id, employee_id):

        query = {
            BaseModel.Fields._ID: _id,
            JobShift.Fields.EMPLOYEE_SHIFTS: {
                '$elemMatch': {EmployeeShift.Fields.EMPLOYEE_ID: employee_id}
            }
        }

        jobshift_dict = DatabaseManager.find(
            Collection.JOBSHIFTS, query, False
        )

        if jobshift_dict:
            return JobShift(**jobshift_dict)


    @staticmethod
    def _can_we_remove_employee_from_jobshift(employee_id,
                                              jobshift_id):
        jobshift = JobOperations.find_jobshift_by_id_and_employee_id(
            jobshift_id, employee_id
        )
        if not jobshift:
            msg = "The employee with _id:%s is not scheduled " \
                  "jobshift with id:%s. Hence it cannot be removed from it" \
                  % (employee_id, jobshift_id)
            raise UserException(msg)


    @staticmethod
    def _can_we_schedule_employee_for_date(employee_id,
                                           check_for_date):
        jobshift = JobOperations.find_jobshift_by_date_and_employee_id(
            employee_id, check_for_date
        )
        if jobshift:
            msg = "We cannot schedule employee for date:%s because the " \
                  "employee is currently scheduled for jobshift _id:%s " \
                  "for that day" % (check_for_date, jobshift._id)

            raise UserException(msg)


    @staticmethod
    def _employee_active_to_be_scheduled(employee_id):
        employee = DatabaseManager.find_object_by_id(
            Collection.EMPLOYEES, employee_id, True
        )
        if not employee.active:
            msg = "Employee with _id:%s is not active, only active " \
                  "employees can be scheduled" % (employee_id,)
            raise UserException(msg)


    @staticmethod
    def _can_we_schedule_employee_for_jobshift(employee_id,
                                               jobshift_id):
        jobshift = JobOperations.find_jobshift_by_id_and_employee_id(
            jobshift_id, employee_id
        )
        if jobshift:
            msg = "Employee _id:%s is already scheduled for" \
                  "jobshift _id:%s" % (employee_id, jobshift_id)
            raise UserException(msg)


    @staticmethod
    def _force_remove_employeeshift(employee_id, jobshift_id):
        query = {
            BaseModel.Fields._ID: jobshift_id
        }
        update = {
            '$pull': {
                JobShift.Fields.EMPLOYEE_SHIFTS: {
                    EmployeeShift.Fields.EMPLOYEE_ID: employee_id
                }
            }
        }
        result = DatabaseManager.update(Collection.JOBSHIFTS,
                                        query, update,
                                        multi=False, upsert=False)
        return result


    @staticmethod
    def _force_add_employeeshift(employee_id, jobshift_id):

        employeeshift_dict = EmployeeShift.encode(
            EmployeeShift(employee_id, None, None, None, None)
        )

        query = {
            BaseModel.Fields._ID: jobshift_id
        }
        update = {
            '$push': {
                JobShift.Fields.EMPLOYEE_SHIFTS: employeeshift_dict
            }
        }
        result = DatabaseManager.update(Collection.JOBSHIFTS,
                                        query, update,
                                        multi=False, upsert=False)
        return result

    @staticmethod
    def add_employee_to_jobshift(employee_id, jobshift_id):
        """
        This method guarantees that the employee can only be added to
        at most one jobshift for each date
        """
        # We check for existence of employee and jobshift
        DatabaseManager.find_object_by_id(
            Collection.EMPLOYEES, employee_id, True
        )
        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        JobOperations._employee_active_to_be_scheduled(employee_id)
        JobOperations._can_we_schedule_employee_for_jobshift(employee_id,
                                                             jobshift_id)
        JobOperations._can_we_schedule_employee_for_date(employee_id,
                                                         jobshift.job_date)

        return JobOperations._force_add_employeeshift(employee_id,
                                                      jobshift_id)

    @staticmethod
    def remove_employee_from_jobshift(employee_id, jobshift_id):
        # We check for existence of employee and jobshift
        DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        DatabaseManager.find_object_by_id(
            Collection.EMPLOYEES, employee_id, True
        )

        # check if we can remove employee from jobshift
        JobOperations._can_we_remove_employee_from_jobshift(
            employee_id, jobshift_id
        )

        return JobOperations._force_remove_employeeshift(employee_id,
                                                         jobshift_id)


    @staticmethod
    def move_employee_amongst_jobshifts(employee_id,
                                        from_jobshift_id,
                                        to_jobshift_id):

        if from_jobshift_id == to_jobshift_id:
            raise UserException("Both jobshift _id's are the same")

        # we check existence of employee and jobshifts
        DatabaseManager.find_object_by_id(
            Collection.EMPLOYEES, employee_id, True
        )
        from_jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, from_jobshift_id, True
        )
        to_jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, to_jobshift_id, True
        )

        JobOperations._can_we_remove_employee_from_jobshift(employee_id,
                                                            from_jobshift_id)

        JobOperations._can_we_schedule_employee_for_jobshift(employee_id,
                                                             to_jobshift_id)

        if from_jobshift.job_date != to_jobshift.job_date:
            JobOperations._can_we_schedule_employee_for_date(
                employee_id, to_jobshift.job_date
            )

        remove_result = JobOperations._force_remove_employeeshift(
            employee_id, from_jobshift_id
        )
        add_result = JobOperations._force_add_employeeshift(
            employee_id, to_jobshift_id
        )
        # todo figure out what to do with the results
        # todo what to do if one fails