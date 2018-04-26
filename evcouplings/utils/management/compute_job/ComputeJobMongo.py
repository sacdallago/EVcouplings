from evcouplings.utils.management.compute_job import ComputeJobInterface, DocumentNotFound, DATABASE_NAME
from pymongo import MongoClient
import datetime

TTL = {
    'month': 60 * 60 * 24 * 31,
    'week': 60 * 60 * 24 * 7,
    'minute': 60
}


class ComputeJobMongo(ComputeJobInterface):

    def job_name(self):
        return self._job_name

    def job_group(self):
        return self._job_group

    def status(self):
        return self._status

    def stage(self):
        return self._stage

    def created_at(self):
        return self._created_at

    def updated_at(self):
        return self._updated_at

    def __init__(self, config):
        super(ComputeJobMongo, self).__init__(config)

        # Get things from management
        self._management = self.config.get("management")
        assert self._management is not None, "You must pass a full config file with a management field"

        self._job_name = self._management.get("job_name")
        assert self._job_name is not None, "config.management must contain a job_name"

        self._job_group = self._management.get("job_group")
        assert self._job_group is not None, "config.management must contain a job_group"

        self._compute_job_uri = self._management.get("compute_job_uri")
        assert self._compute_job_uri is not None, "compute_job_uri must be defined"

        self._status = "initialized"
        self._stage = "initialized"
        self._created_at = datetime.datetime.now()
        self._updated_at = datetime.datetime.now()

        # Connect to mongo and get URI database
        client = MongoClient(self._compute_job_uri)
        db = client.get_default_database()
        collection = db[DATABASE_NAME]

        # Will expire the document after time is > than updated_at + TTL
        collection.ensure_index("updated_at", expireAfterSeconds=TTL.get('month'))

        q = collection.find_one({
            '_id': self._job_name
        })

        if q is None:
            collection.insert_one({
                "_id": self._job_name,
                "job_name": self._job_name,
                "job_group": self._job_group,
                "created_at": self._created_at,
                "updated_at": self._updated_at,
                "status": self._status,
                "stage": self._stage
            })
        else:
            self._created_at = q['created_at']
            self._updated_at = q['updated_at']
            self._status = q['status']
            self._stage = q['stage']

        client.close()

    def update_job_status(self, status=None, stage=None):
        update = {}

        if stage is not None:
            self._stage = stage
            update['stage'] = self._stage
        elif status is not None:
            self._status = status
            update['status'] = self._status

        self._updated_at = datetime.datetime.now()
        update['updated_at'] = self._updated_at

        # Connect to mongo and get URI database
        client = MongoClient(self._compute_job_uri)
        db = client.get_default_database()
        collection = db[DATABASE_NAME]

        q = collection.find_one({"_id": self._job_name})

        if q is None:
            raise DocumentNotFound()

        collection.update_one({
            '_id': q.get("job_name")
        }, {
            "$set": update
        }, upsert=False)

        client.close()

        return q

    @staticmethod
    def get_job(job_id, connection_string):
        # Connect to mongo and get URI database
        client = MongoClient(connection_string)
        db = client.get_default_database()
        collection = db[DATABASE_NAME]

        q = collection.find_one({
            '_id': job_id
        })

        return q

    @staticmethod
    def get_jobs_from_group(group_id, connection_string):
        # Connect to mongo and get URI database
        client = MongoClient(connection_string)
        db = client.get_default_database()
        collection = db[DATABASE_NAME]

        q = collection.find({
            'job_group': group_id
        })

        return list(q)