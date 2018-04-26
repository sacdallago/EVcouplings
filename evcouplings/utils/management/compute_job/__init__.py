from evcouplings.utils.management.compute_job import ComputeJobMongo
from evcouplings.utils.management.compute_job import ComputeJobSQL
from evcouplings.utils.management.compute_job import ComputeJobLocal


"""
Status of job. Resolves to string
"""
EStatus = (lambda **enums: type('Enum', (), enums))(
    INIT="initialized",
    PEND="pending",
    RUN="running",
    DONE="done",
    FAIL="failed",  # job failed due to bug
    TERM="terminated",  # job was terminated externally
)

"""
Tracker types. Default and fallback is "local"
"""
COMPUTE_JOB_TRACKER = {
    "local": ComputeJobLocal,
    "sql": ComputeJobSQL,
    "mongo": ComputeJobMongo
}


def get_compute_job_tracker(config):
    """
    Based on config, get back the type of job tracker.

    Will check management.compute_job.type
    :param config: The complete job config (not flattened)
    :return: Object implementing functions of the ComputeJobInterface class
    """

    # Fallback mechanism: if management not defined, or if compute_job in management not defined: use local
    compute_job = config\
        .get("management", {})\
        .get("compute_job_type", "local")

    return COMPUTE_JOB_TRACKER.get(compute_job)(config)