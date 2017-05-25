from data.models import Job, JobOutputDir, JobInputFile, DDSJobInputFile
from rest_framework.exceptions import ValidationError
from util import get_file_name
from exceptions import JobFactoryException
import json



def create_job_factory(job_answer_set):
    """
    Create JobFactory based on questions and answers referenced by job_answer_set.
    :param user: User: user who's credentials we will use for building the job
    :param job_answer_set: JobAnswerSet: references questions and their answers to use for building a Job.
    :return: JobFactory
    """
    user = job_answer_set.user
    workflow_version = job_answer_set.questionnaire.workflow_version
    user_job_order_dict = json.loads(job_answer_set.user_job_order)
    system_job_order_dict = json.loads(job_answer_set.questionnaire.system_job_order)
    job_name = job_answer_set.job_name
    vm_project_name = job_answer_set.questionnaire.vm_project.vm_project_name
    vm_flavor = job_answer_set.questionnaire.vm_flavor.vm_flavor

    factory = JobFactory(user, workflow_version, user_job_order_dict, system_job_order_dict, job_name, vm_project_name,
                         vm_flavor)

    return factory


class JobFactory(object):
    """
    Creates Job record in the database based on questions their answers.
    """
    def __init__(self, user, workflow_version, user_job_order, system_job_order, job_name, vm_project_name,
                 vm_flavor):
        """
        Setup factory
        :param user: User: user we are creating this job for and who's credentials we will use
        :param workflow_version: WorkflowVersion: which CWL workflow are we building a job for
        """
        self.workflow_version = workflow_version
        self.user = user
        self.user_job_order = user_job_order
        self.system_job_order = system_job_order
        self.job_name = job_name
        self.vm_project_name = vm_project_name
        self.vm_flavor = vm_flavor

    def create_job(self):
        """
        Create a job based on the workflow_version, system job order and user job order
        :return: Job: job that was inserted into the database along with it's output directory and input files.
        """

        if self.system_job_order is None or self.user_job_order is None:
            raise JobFactoryException('Attempted to create a job without specifying system job order or user job order')

        # Create the job order to be submitted. Begin with the system info and overlay the user order
        job_order = self.system_job_order.copy()
        job_order.update(self.user_job_order)
        job = Job.objects.create(workflow_version=self.workflow_version,
                                 user=self.user,
                                 name=self.job_name,
                                 vm_project_name=self.vm_project_name,
                                 vm_flavor=self.vm_flavor,
                                 job_order=json.dumps(job_order)
        )
        # TODO: Create JobOutputDir
        # TODO: Populate JobInputFiles
        return job

