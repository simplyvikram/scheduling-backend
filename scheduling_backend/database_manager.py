
from flask import current_app
from models import (
    BaseModel, Client, Job, Employee, Equipment,
    EmployeeShift, EquipmentShift, JobShift
)
from exceptions import UserException

class Collection(object):
    EMPLOYEES = 'employees'
    CLIENTS = 'clients'
    EQUIPMENT = 'equipment'
    JOBS = 'jobs'
    JOBSHIFTS = 'jobshifts'

class DatabaseManager(object):

    @staticmethod
    def find(collection_name, query_dict={}, multiple=False):
        """
        Retuns a dict/list containing the document/documents found in db
        """


        if multiple:
            docs = current_app.db[collection_name].find(query_dict)
            return list(docs)
        else:
            doc = current_app.db[collection_name].find_one(query_dict)
            return doc

    @staticmethod
    def find_count(collection_name, query_dict={}):
        return current_app.db[collection_name].find(query_dict).count()

    @staticmethod
    def insert(collection_name, _dict_or_list):
        """
        We insert a single document or a list of documents in the db
        """

        return current_app.db[collection_name].insert(_dict_or_list)


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

        return DatabaseManager.convert_document_to_object(
            collection_name, document
        )


    @staticmethod
    def find_documents_by_ids(collection_name, _id_list):
        query = {
            BaseModel.Fields._ID: {'$in': _id_list}
        }
        documents = DatabaseManager.find(collection_name, query, multiple=True)
        return documents

    @staticmethod
    def find_objects_by_ids(collection_name, _id_list):
        documents = DatabaseManager.find_documents_by_ids(
            collection_name, _id_list
        )

        objects = map(
            lambda document: DatabaseManager.convert_document_to_object(
                collection_name, document
            ),
            documents
        )
        return objects


    @staticmethod
    def convert_document_to_object(collection_type, document):
        _dict = {

            Collection.JOBSHIFTS: JobShift,
            Collection.EMPLOYEES: Employee,
            Collection.EQUIPMENT: Equipment,
            Collection.CLIENTS: Client,
            Collection.JOBS: Job
        }
        return _dict[collection_type](**document)



class JobOperations(object):


    @staticmethod
    def find_jobshift_ids_for_day(date_str):

        d = current_app.db[Collection.JOBSHIFTS].aggregate(
            [
                {
                    '$match': {JobShift.Fields.JOB_DATE: date_str}
                }
                ,
                {
                    '$project': {BaseModel.Fields._ID: 1}
                }
            ]
        )
        result = d['result']

        result = map(lambda x: x[BaseModel.Fields._ID],
                     result)

        return result


    @staticmethod
    def find_jobshifts(dates_strings=None, job_id=None,
                       employee_id=None, equipment_id=None):
        """
        At least one key value argument needs to be present, else an exception
        is thrown
        """

        an_arg_is_present = bool(dates_strings) or bool(job_id) or \
                            bool(employee_id) or bool(equipment_id)
        if not an_arg_is_present:
            raise UserException("Jobshift search needs to be narrowed down")

        query = dict()

        if dates_strings:
            query[JobShift.Fields.JOB_DATE] = {'$in': dates_strings}
        if job_id:
            query[JobShift.Fields.JOB_ID] = job_id
        if employee_id:
            query[JobShift.Fields.EMPLOYEE_SHIFTS] = {
                '$elemMatch': {EmployeeShift.Fields.EMPLOYEE_ID: employee_id}
            }
        if equipment_id:
            query[JobShift.Fields.EQUIPMENT_SHIFTS] = {
                '$elemMatch': {EquipmentShift.Fields.EQUIPMENT_ID: equipment_id}
            }

        jobshifts_documents = DatabaseManager.find(
            Collection.JOBSHIFTS, query, multiple=True
        )
        jobshifts = map(lambda document: JobShift(**document),
                        jobshifts_documents)

        return jobshifts

    @staticmethod
    def delete_jobshifts(jobshift_ids):

        remove_query_dict = dict()
        remove_query_dict[BaseModel._id] = {'$in': jobshift_ids}

        DatabaseManager.remove(
            Collection.JOBSHIFTS,
            remove_query_dict,
            multiple=True
        )



    @staticmethod
    def _can_we_remove_employee_from_jobshift(employee_id,
                                              jobshift_id):
        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        if not jobshift.contains_employee(employee_id):

            msg = "Employee {employee_id} is not scheduled for " \
                  "jobshift {jobshift_id}. Hence it cannot be removed " \
                  "from it".format(employee_id=employee_id,
                                   jobshift_id=jobshift_id)
            raise UserException(msg)

    @staticmethod
    def _can_we_remove_equipment_from_jobshift(equipment_id, jobshift_id):
        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        if not jobshift.contains_equipment(equipment_id):
            msg = "Equipment {equipment_id} is not scheduled for " \
                  "jobshift {jobshift_id}. Hence it cannot be removed " \
                  "from it".format(equipment_id=equipment_id,
                                   jobshift_id=jobshift_id)
            raise UserException(msg)



    @staticmethod
    def _can_we_schedule_employee_for_date(employee_id,
                                           date_str):

        date_strings = [date_str]
        jobshifts = JobOperations.find_jobshifts(dates_strings=date_strings,
                                                 employee_id=employee_id)

        if len(jobshifts) > 0:
            msg = "We cannot schedule employee {employee_id} for " \
                  "date {date_str}, as for that day its already scheduled " \
                  "for jobshift {jobshift_id}".format(
                employee_id=employee_id,
                date_str=date_str,
                jobshift_id=jobshifts[0]._id
            )

            raise UserException(msg)

    @staticmethod
    def _can_we_schedule_equipment_for_date(equipment_id, date_str):

        date_strings = [date_str]
        jobshifts = JobOperations.find_jobshifts(dates_strings=date_strings,
                                                 equipment_id=equipment_id)
        if len(jobshifts) > 0:
            msg = "We cannot schedule equipment {equipment_id} for " \
                  "date {date_str}, as for that day its already scheduled " \
                  "for jobshift {jobshift_id}".format(
                equipment_id=equipment_id,
                date_str=date_str,
                jobshift_id=jobshifts[0]._id
            )

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
    def _can_we_schedule_employee_for_jobshift(employee_id, jobshift_id):

        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        if jobshift.contains_employee(employee_id):
            msg = "Employee {employee_id} is already scheduled for " \
                  "jobshift {jobshift_id}".format(employee_id=employee_id,
                                                  jobshift_id=jobshift_id)
            raise UserException(msg)


    @staticmethod
    def _can_we_schedule_equipment_for_jobshift(equipment_id, jobshift_id):

        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        if jobshift.contains_equipment(equipment_id):
            msg = "Equipment {equipment_id} is already scheduled for " \
                  "jobshift {jobshift_id}".format(equipment_id=equipment_id,
                                                  jobshift_id=jobshift_id)


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
        result = DatabaseManager.update(
            Collection.JOBSHIFTS, query, update, multi=False, upsert=False
        )
        return result


    @staticmethod
    def _force_remove_equipmentshift(equipment_id, jobshift_id):
        query = {
            BaseModel.Fields._ID: jobshift_id
        }
        update = {
            '$pull': {
                JobShift.Fields.EQUIPMENT_SHIFTS: {
                    EquipmentShift.Fields.EQUIPMENT_ID: equipment_id
                }
            }
        }
        result = DatabaseManager.update(
            Collection.JOBSHIFTS, query, update, multi=False, upsert=False)
        return result

    @staticmethod
    def _force_add_employeeshift(employee_id, jobshift_id, shift_role):

        employeeshift_dict = EmployeeShift.encode(
            EmployeeShift(employee_id, shift_role, None, None, None, None)
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
    def _force_add_equipment_shift(equipment_id, jobshift_id):

        equipmentshift_dict = EquipmentShift.encode(
            EquipmentShift(equipment_id)
        )
        query = {
            BaseModel.Fields._ID: jobshift_id
        }
        update = {
            '$push': {
                JobShift.Fields.EQUIPMENT_SHIFTS: equipmentshift_dict
            }
        }
        result = DatabaseManager.update(
            Collection.JOBSHIFTS, query, update, multi=False, upsert=False
        )
        return result


    @staticmethod
    def modify_employee_shift(employee_id, jobshift_id, data):
        """
        Update only one employeeshift in a jobshift,
        and that too with the relevant data

        Based on
        http://mongoblog.tumblr.com/post/21792332279/updating-one-element-in-an-array
        """
        query_key_prefix = JobShift.Fields.EMPLOYEE_SHIFTS + "."
        update_key_prefix = JobShift.Fields.EMPLOYEE_SHIFTS + ".$."

        query = {
            BaseModel.Fields._ID: jobshift_id,
            query_key_prefix + EmployeeShift.Fields.EMPLOYEE_ID: employee_id
        }

        update_dict = dict()
        for key, value in data.iteritems():
            update_dict[update_key_prefix + key] = value

        update = {
            "$set": update_dict
        }

        DatabaseManager.update(Collection.JOBSHIFTS,
                               query,
                               update,
                               multi=False,
                               upsert=False)


    @staticmethod
    def add_employee_to_jobshift(employee_id, jobshift_id, shift_role):
        """
        This method guarantees that the employee can only be added to
        at most one jobshift for each date
        """
        # We check for existence of employee and jobshift
        employee = DatabaseManager.find_object_by_id(
            Collection.EMPLOYEES, employee_id, True
        )
        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        if not shift_role:
            shift_role = employee.current_role

        JobOperations._employee_active_to_be_scheduled(employee_id)
        JobOperations._can_we_schedule_employee_for_jobshift(employee_id,
                                                             jobshift_id)
        JobOperations._can_we_schedule_employee_for_date(employee_id,
                                                         jobshift.job_date)

        return JobOperations._force_add_employeeshift(
            employee_id, jobshift_id, shift_role
        )

    @staticmethod
    def add_equipment_to_jobshift(equipment_id, jobshift_id):

        # We check for existence of both equipment and jobshift
        equipment = DatabaseManager.find_object_by_id(
            Collection.EQUIPMENT, equipment_id, True
        )
        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        JobOperations._can_we_schedule_equipment_for_jobshift(equipment_id,
                                                              jobshift_id)
        JobOperations._can_we_schedule_equipment_for_date(equipment_id,
                                                          jobshift.job_date)
        JobOperations._force_add_equipment_shift(equipment_id, jobshift_id)

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
    def remove_equipment_from_jobshift(equipment_id, jobshift_id):
        DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        DatabaseManager.find_object_by_id(
            Collection.EQUIPMENT, equipment_id, True
        )

        JobOperations._can_we_remove_equipment_from_jobshift(
            equipment_id, jobshift_id
        )
        return JobOperations._force_remove_equipmentshift(equipment_id,
                                                          jobshift_id)


    @staticmethod
    def move_employee_amongst_jobshifts(employee_id,
                                        from_jobshift_id,
                                        to_jobshift_id,
                                        shift_role):

        if from_jobshift_id == to_jobshift_id:
            raise UserException("Both jobshift _id's are the same")

        # we check existence of employee and jobshifts
        employee = DatabaseManager.find_object_by_id(
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

        if not shift_role:
            shift_role = employee.current_role

        remove_result = JobOperations._force_remove_employeeshift(
            employee_id, from_jobshift_id
        )
        add_result = JobOperations._force_add_employeeshift(
            employee_id, to_jobshift_id, shift_role
        )
        # todo figure out what to do with the results
        # todo what to do if one above force_add/force_remove operation fails


    @staticmethod
    def move_equipment_amongst_jobshifts(equipment_id,
                                         from_jobshift_id,
                                         to_jobshift_id):

        if from_jobshift_id == to_jobshift_id:
            raise UserException("Both jobshift _id's are the same")

        # we check existence of employee and jobshifts
        equipment = DatabaseManager.find_object_by_id(
            Collection.EQUIPMENT, equipment_id, True
        )
        from_jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, from_jobshift_id, True
        )
        to_jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, to_jobshift_id, True
        )

        JobOperations._can_we_remove_equipment_from_jobshift(equipment_id,
                                                             from_jobshift_id)
        JobOperations._can_we_schedule_equipment_for_jobshift(equipment_id,
                                                              to_jobshift_id)

        if from_jobshift.job_date != to_jobshift.job_date:
            JobOperations._can_we_schedule_equipment_for_date(
                equipment_id, to_jobshift.job_date
            )

        remove_result = JobOperations._force_remove_equipmentshift(
            equipment_id, from_jobshift_id
        )
        add_result = JobOperations._force_add_equipment_shift(
            equipment_id, to_jobshift_id
        )

        # todo figure out what to do with the results
        # what if one of the above force_add/force_remove operation fails

