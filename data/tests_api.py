from django.contrib.auth.models import User as django_user
from django.core.urlresolvers import reverse
from mock.mock import MagicMock, patch, Mock
from rest_framework import status
from rest_framework.test import APITestCase
import json

from data.models import Workflow, WorkflowVersion, Job, JobInputFile, JobError, \
    DDSUserCredential, DDSEndpoint, DDSJobInputFile, URLJobInputFile, JobOutputDir, \
    JobQuestionnaire, JobAnswerSet, VMFlavor, VMProject
from exceptions import WrappedDataServiceException
from util import DDSResource


class UserLogin(object):
    """
    Wraps up different user states for tests.
    """
    def __init__(self, client):
        self.client = client

    def become_unauthorized(self):
        self.client.logout()

    def become_normal_user(self):
        username = "user"
        password = "resu"
        user = django_user.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)
        return user

    def become_other_normal_user(self):
        username = "user2"
        password = "resu2"
        user = django_user.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)
        return user

    def become_admin_user(self):
        username = "myadmin"
        password = "nimda"
        user = django_user.objects.create_superuser(username=username, email='', password=password)
        self.client.login(username=username, password=password)
        return user


class DDSProjectsTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        self.user_login.become_normal_user()

    def testFailsUnauthenticated(self):
        self.user_login.become_unauthorized()
        url = reverse('dds-projects-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('data.api.get_user_projects')
    def testListProjects(self, mock_get_user_projects):
        mock_get_user_projects.return_value = [Mock(id='abc123'), Mock(id='def567')]
        url = reverse('dds-projects-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    @patch('data.api.get_user_project')
    def testRetrieveProject(self, mock_get_user_project):
        project_id = 'abc123'
        mock_dds_project = Mock()
        # name is special on instantiation, so configure()
        mock_dds_project.configure_mock(id=project_id, name='ProjectA')
        mock_get_user_project.return_value = mock_dds_project
        url = reverse('dds-projects-list') + project_id + '/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'ProjectA')

    @patch('data.api.get_user_project')
    def testRetrieveProjectNotFound(self, mock_get_user_project):
        project_id = 'abc123'
        dds_error = MagicMock()
        dds_error.status_code = 404
        dds_error.message = 'Not Found'
        mock_get_user_project.side_effect = WrappedDataServiceException(dds_error)
        url = reverse('dds-projects-list') + project_id + '/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DDSResourcesTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        self.user_login.become_normal_user()

    def testFailsUnauthenticated(self):
        self.user_login.become_unauthorized()
        url = reverse('dds-resources-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('data.api.get_user_project_content')
    def testListsResourcesByProject(self, mock_get_user_project_content):
        project_id = 'abc123'
        resource  = {'id': '12355','name': 'test.txt', 'project': {'id': project_id}, 'parent': {'kind': 'dds-project', 'id': project_id}}
        mock_get_user_project_content.return_value = DDSResource.from_list([resource])
        url = reverse('dds-resources-list')
        response = self.client.get(url, data={'project_id': project_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('data.api.get_user_folder_content')
    def testListsResourcesByFolder(self, mock_get_user_folder_content):
        project_id = 'abc123'
        folder_id = 'def456'
        resource = {'id': '12355', 'name': 'test.txt', 'project': {'id': project_id}, 'parent': {'kind': 'dds-folder', 'id': folder_id}}
        mock_get_user_folder_content.return_value = DDSResource.from_list([resource])
        url = reverse('dds-resources-list')
        response = self.client.get(url, data={'folder_id': folder_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('data.api.get_user_project_content')
    def testFailsWhenProjectNotFound(self, mock_get_user_project_content):
        project_id = 'abc123'
        dds_error = MagicMock()
        dds_error.status_code = 404
        dds_error.message = 'Not Found'
        mock_get_user_project_content.side_effect = WrappedDataServiceException(dds_error)
        url = reverse('dds-resources-list')
        response = self.client.get(url, data={'project_id': project_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def testFailsWithoutProjectOrFolderID(self):
        url = reverse('dds-resources-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('data.api.get_user_project_content')
    def testIncludesFileDetailsForFiles(self, mock_get_user_project_content):
        project_id = 'abc123'
        file_resource = {
            'id': 'file2',
            'kind': 'dds-file',
            'name': 'file-with-details.txt',
            'project': {
                'id': project_id
            },
            'parent': {
                'kind': 'dds-project',
                'id': project_id
            },
            'current_version': {
                'id': 'v2',
                'version': 2,
                'upload': {
                    'id': 'u1',
                    'size': 1048576,
                }
            }
        }
        mock_get_user_project_content.return_value = DDSResource.from_list([file_resource])
        url = reverse('dds-resources-list')
        response = self.client.get(url, data={'project_id': project_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['version'], 2)
        self.assertEqual(response.data[0]['version_id'], 'v2')
        self.assertEqual(response.data[0]['size'], 1048576)

    @patch('data.api.get_user_project_content')
    def testDoesNotIncludeFileDetailsForFolders(self, mock_get_user_project_content):
        project_id = 'abc123'
        folder_resource = {
            'id': 'f2',
            'kind': 'dds-folder',
            'name': 'folder2',
            'project': {
                'id': project_id
            },
            'parent': {
                'kind': 'dds-project',
                'id': project_id
            }
        }
        mock_get_user_project_content.return_value = DDSResource.from_list([folder_resource])
        url = reverse('dds-resources-list')
        response = self.client.get(url, data={'project_id': project_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIsNone(response.data[0]['version'])
        self.assertIsNone(response.data[0]['version_id'])
        self.assertEqual(response.data[0]['size'], 0)


class DDSEndpointTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)

    def testNoPermissionsWithoutAuth(self):
        self.user_login.become_unauthorized()
        url = reverse('ddsendpoint-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DDSUserCredentialTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        self.endpoint = DDSEndpoint.objects.create(name='DukeDS', agent_key='secret',
                                                   api_root='https://someserver.com/api')

    def testNoPermissionsWithoutAuth(self):
        self.user_login.become_unauthorized()
        url = reverse('ddsusercredential-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testUserOnlySeeAllCredsButNoTokens(self):
        """
        Normal users should not be able to see tokens but can pick from available credentials.
        """
        other_user = self.user_login.become_other_normal_user()
        user = self.user_login.become_normal_user()
        self.cred = DDSUserCredential.objects.create(endpoint=self.endpoint, user=user, token='secret1',
                                                    dds_id='1')
        self.cred = DDSUserCredential.objects.create(endpoint=self.endpoint, user=other_user, token='secret2',
                                                     dds_id='2')
        self.assertEqual(2, len(DDSUserCredential.objects.all()))

        url = reverse('ddsusercredential-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        self.assertEqual({'id': 1, 'user': 2, 'endpoint': 1}, response.data[0])
        self.assertEqual({'id': 2, 'user': 1, 'endpoint': 1}, response.data[1])

    def testUserCantCreate(self):
        user = self.user_login.become_normal_user()
        url = reverse('ddsusercredential-list')
        response = self.client.post(url, format='json', data={
            'endpoint': self.endpoint.id,
            'token': '12309ufwlkjasdf',
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class WorkflowTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)

    def testNoPermissionsWithoutAuth(self):
        self.user_login.become_unauthorized()
        url = reverse('workflow-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testReadOnlyForAuthUser(self):
        self.user_login.become_normal_user()
        url = reverse('workflow-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(url, format='json', data={'name': 'RnaSeq'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class WorkflowVersionTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)

    def testNoPermissionsWithoutAuth(self):
        self.user_login.become_unauthorized()
        url = reverse('workflowversion-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testReadOnlyForAuthUser(self):
        self.user_login.become_normal_user()
        url = reverse('workflowversion-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class JobsTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)

    def testUserOnlySeeTheirData(self):
        url = reverse('job-list')
        normal_user = self.user_login.become_normal_user()
        response = self.client.post(url, format='json',
                                    data={
                                        'name': 'my job',
                                        'workflow_version': self.workflow_version.id,
                                        'vm_project_name': 'jpb67',
                                        'job_order': '{}',
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertEqual(normal_user.id, response.data[0]['user'])
        self.assertEqual('my job', response.data[0]['name'])
        self.assertEqual(self.workflow_version.id, response.data[0]['workflow_version'])

        other_user = self.user_login.become_other_normal_user()
        response = self.client.post(url, format='json',
                            data={
                                'name': 'my job2',
                                'workflow_version': self.workflow_version.id,
                                'vm_project_name': 'jpb88',
                                'job_order': '{}',
                            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertEqual(other_user.id, response.data[0]['user'])
        self.assertEqual(self.workflow_version.id, response.data[0]['workflow_version'])

    def testAdminSeeAllData(self):
        url = reverse('job-list')
        normal_user = self.user_login.become_normal_user()
        response = self.client.post(url, format='json',
                                    data={
                                        'name': 'my job',
                                        'workflow_version': self.workflow_version.id,
                                        'vm_project_name': 'jpb67',
                                        'job_order': '{}',
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # normal user can't see admin endpoint
        url = reverse('admin_job-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        other_user = self.user_login.become_other_normal_user()
        url = reverse('job-list')
        response = self.client.post(url, format='json',
                            data={
                                'name': 'my job2',
                                'workflow_version': self.workflow_version.id,
                                'vm_project_name': 'jpb88',
                                'job_order': '{}',
                            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # admin user can see both via admin endpoint
        admin_user = self.user_login.become_admin_user()
        url = reverse('admin_job-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        self.assertIn(other_user.id, [item['user_id'] for item in response.data])
        self.assertIn(normal_user.id, [item['user_id'] for item in response.data])
        self.assertIn('my job', [item['name'] for item in response.data])
        self.assertIn('my job2', [item['name'] for item in response.data])
        self.assertEqual(['RnaSeq', 'RnaSeq'], [item['workflow_version']['name'] for item in response.data])

    def testNormalUserSeeErrors(self):
        normal_user = self.user_login.become_normal_user()
        job = Job.objects.create(name='somejob',
                                 workflow_version=self.workflow_version,
                                 vm_project_name='jpb67',
                                 job_order={},
                                 user=normal_user)
        JobError.objects.create(job=job, content='Err1', job_step='R')
        JobError.objects.create(job=job, content='Err2', job_step='R')
        url = reverse('job-list') + '{}/'.format(job.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job_errors_content = [job_error['content'] for job_error in response.data['job_errors']]
        self.assertEqual(2, len(job_errors_content))
        self.assertIn('Err1', job_errors_content)
        self.assertIn('Err2', job_errors_content)

    def testStopRegularUserFromSettingStateOrStep(self):
        """
        Only admin should change job state or job step.
        """
        url = reverse('job-list')
        normal_user = self.user_login.become_normal_user()
        response = self.client.post(url, format='json',
                                    data={
                                        'name': 'my job',
                                        'workflow_version': self.workflow_version.id,
                                        'vm_project_name': 'jpb67',
                                        'job_order': '{}',
                                        'state': Job.JOB_STATE_FINISHED,
                                        'step': Job.JOB_STEP_RUNNING,
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job = Job.objects.first()
        self.assertEqual(Job.JOB_STATE_NEW, job.state)
        self.assertEqual(None, job.step)

    def testAdminUserUpdatesStateAndStep(self):
        """
        Admin should be able to change job state and job step.
        """
        admin_user = self.user_login.become_admin_user()
        job = Job.objects.create(name='somejob',
                                 workflow_version=self.workflow_version,
                                 vm_project_name='jpb67',
                                 job_order={},
                                 user=admin_user)
        url = reverse('admin_job-list') + '{}/'.format(job.id)
        response = self.client.put(url, format='json',
                                    data={
                                        'state': Job.JOB_STATE_RUNNING,
                                        'step': Job.JOB_STEP_CREATE_VM,
                                    })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job = Job.objects.first()
        self.assertEqual(Job.JOB_STATE_RUNNING, job.state)
        self.assertEqual(Job.JOB_STEP_CREATE_VM, job.step)

    @patch('data.lando.LandoJob._make_client')
    def test_job_start(self, mock_make_client):
        normal_user = self.user_login.become_normal_user()
        job = Job.objects.create(workflow_version=self.workflow_version,
                                 vm_project_name='jpb67',
                                 job_order={},
                                 user=normal_user)

        url = reverse('job-list') + str(job.id) + '/start/'

        # Post to /start/ for job in NEW state should work
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], Job.JOB_STATE_STARTING)

        # Post to /start/ for job in RUNNING state should fail
        job.state = Job.JOB_STATE_RUNNING
        job.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('data.lando.LandoJob._make_client')
    def test_job_cancel(self, mock_make_client):
        normal_user = self.user_login.become_normal_user()
        job = Job.objects.create(workflow_version=self.workflow_version,
                                 vm_project_name='jpb67',
                                 job_order={},
                                 user=normal_user)
        url = reverse('job-list') + str(job.id) + '/cancel/'
        # Post to /cancel/ for job should work
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], Job.JOB_STATE_CANCELING)

    @patch('data.lando.LandoJob._make_client')
    def test_job_restart(self, mock_make_client):
        normal_user = self.user_login.become_normal_user()
        job = Job.objects.create(workflow_version=self.workflow_version,
                                 vm_project_name='jpb67',
                                 job_order={},
                                 user=normal_user)
        url = reverse('job-list') + str(job.id) + '/restart/'

        # Post to /restart/ for job in NEW state should fail (user should use /start/)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_make_client().restart_job.assert_not_called()

        # Post to /restart/ for job in ERROR state should work
        job.state = Job.JOB_STATE_ERROR
        job.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], Job.JOB_STATE_RESTARTING)
        mock_make_client().restart_job.assert_called_with(str(1))

        # Post to /restart/ for job in CANCEL state should work
        job.state = Job.JOB_STATE_CANCEL
        job.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testJobAutoFillsInUser(self):
        url = reverse('job-list')
        normal_user = self.user_login.become_normal_user()
        response = self.client.post(url, format='json',
                                    data={
                                        'name': 'my job',
                                        'workflow_version': self.workflow_version.id,
                                        'vm_project_name': 'jpb67',
                                        'job_order': '{}',
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job = Job.objects.first()
        self.assertEqual(job.user, normal_user)


class JobInputFilesTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)

    def testOnlySeeOwnJobInputFiles(self):
        other_user = self.user_login.become_normal_user()
        other_job = Job.objects.create(workflow_version=self.workflow_version,
                                       vm_project_name='test',
                                       job_order='{}',
                                       user=other_user)
        JobInputFile.objects.create(job=other_job, file_type='dds_file', workflow_name='models')
        this_user = self.user_login.become_other_normal_user()
        this_job = Job.objects.create(workflow_version=self.workflow_version,
                                      vm_project_name='test',
                                      job_order='{}',
                                      user=this_user)
        JobInputFile.objects.create(job=this_job, file_type='dds_file', workflow_name='data1')

        # User endpoint only shows current user's data
        url = reverse('jobinputfile-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

        # Admin endpoint shows all user's data
        self.user_login.become_admin_user()
        url = reverse('admin_jobinputfile-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))


class JobErrorTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)

    def testNormalUserReadOnly(self):
        other_user = self.user_login.become_normal_user()
        other_job = Job.objects.create(workflow_version=self.workflow_version,
                                       vm_project_name='test',
                                       job_order='{}',
                                       user=other_user)
        JobError.objects.create(job=other_job, content='Out of memory.', job_step=Job.JOB_STEP_RUNNING)
        # Normal user can't write
        url = reverse('joberror-list')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        my_user = self.user_login.become_other_normal_user()
        my_job = Job.objects.create(workflow_version=self.workflow_version,
                                       vm_project_name='test',
                                       job_order='{}',
                                       user=my_user)
        JobError.objects.create(job=my_job, content='Out of memory.', job_step=Job.JOB_STEP_RUNNING)

        # User endpoint only shows current user's data
        url = reverse('joberror-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

        # Admin endpoint shows all user's data
        self.user_login.become_admin_user()
        url = reverse('admin_joberror-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))

    def testNormalEndpointNoWrite(self):
        self.user_login.become_normal_user()
        url = reverse('joberror-list')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def testAdminEndpointCanWrite(self):
        my_user = self.user_login.become_admin_user()
        my_job = Job.objects.create(workflow_version=self.workflow_version,
                                       vm_project_name='test',
                                       job_order='{}',
                                       user=my_user)
        url = reverse('admin_joberror-list')
        response = self.client.post(url, format='json', data={
            'job': my_job.id,
            'content': 'oops',
            'job_step': Job.JOB_STEP_CREATE_VM,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(1, len(JobError.objects.all()))


class DDSJobInputFileTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)
        self.other_user = self.user_login.become_other_normal_user()
        self.my_user = self.user_login.become_normal_user()
        self.my_job = Job.objects.create(workflow_version=self.workflow_version,
                                       vm_project_name='test',
                                       job_order='{}',
                                       user=self.my_user)
        self.job_input_file = JobInputFile.objects.create(job=self.my_job, file_type='dds_file', workflow_name='data1')
        endpoint = DDSEndpoint.objects.create(name='DukeDS', agent_key='secret', api_root='https://someserver.com/api')
        self.cred = DDSUserCredential.objects.create(endpoint=endpoint, user=self.my_user, token='secret2', dds_id='1')
        self.other_cred = DDSUserCredential.objects.create(endpoint=endpoint, user=self.other_user, token='secret3',
                                                           dds_id='2')

    def testPostAndRead(self):
        url = reverse('ddsjobinputfile-list')
        response = self.client.post(url, format='json', data={
            'job_input_file': self.job_input_file.id,
            'project_id': '12356',
            'file_id': '345987',
            'dds_user_credentials': self.cred.id,
            'destination_path': 'data.txt',
            'index': '1',

        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(1, len(DDSJobInputFile.objects.all()))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertEqual('data.txt', response.data[0]['destination_path'])

    def testUsingOthersCreds(self):
        url = reverse('ddsjobinputfile-list')
        response = self.client.post(url, format='json', data={
            'job_input_file': self.job_input_file.id,
            'project_id': '12356',
            'file_id': '345987',
            'dds_user_credentials': self.other_cred.id,
            'destination_path': 'data.txt',
            'index': '1',

        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class URLJobInputFileTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)
        self.my_user = self.user_login.become_normal_user()
        self.my_job = Job.objects.create(workflow_version=self.workflow_version,
                                         vm_project_name='test',
                                         job_order='{}',
                                         user=self.my_user)
        self.job_input_file = JobInputFile.objects.create(job=self.my_job, file_type='dds_file', workflow_name='data1')

    def testPostAndRead(self):
        url = reverse('urljobinputfile-list')
        response = self.client.post(url, format='json', data={
            'job_input_file': self.job_input_file.id,
            'url': 'http://stuff.com/data.txt',
            'destination_path': 'data.txt',
            'index': '1',

        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(1, len(URLJobInputFile.objects.all()))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertEqual('http://stuff.com/data.txt', response.data[0]['url'])


class JobOutputDirTestCase(APITestCase):
    def setUp(self):
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)
        self.other_user = self.user_login.become_other_normal_user()
        self.my_user = self.user_login.become_normal_user()
        self.my_job = Job.objects.create(workflow_version=self.workflow_version,
                                         vm_project_name='test',
                                         job_order='{}',
                                         user=self.my_user)

        self.endpoint = DDSEndpoint.objects.create(name='DukeDS', agent_key='secret', api_root='https://someserver.com/api')
        self.cred = DDSUserCredential.objects.create(endpoint=self.endpoint, user=self.my_user, token='secret2',
                                                     dds_id='1')
        self.others_cred = DDSUserCredential.objects.create(endpoint=self.endpoint, user=self.other_user,
                                                            token='secret3', dds_id='2')

    def test_list_dirs(self):
        JobOutputDir.objects.create(job=self.my_job, dir_name='results', project_id='1',
                                    dds_user_credentials=self.cred)
        url = reverse('joboutputdir-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        job_output_dir = response.data[0]
        self.assertEqual(self.my_job.id, job_output_dir['job'])
        self.assertEqual('results', job_output_dir['dir_name'])
        self.assertEqual('1', job_output_dir['project_id'])
        self.assertEqual(self.cred.id, job_output_dir['dds_user_credentials'])

    def test_create(self):
        url = reverse('joboutputdir-list')
        response = self.client.post(url, format='json', data={
            'job': self.my_job.id,
            'dir_name': 'results',
            'project_id': '123',
            'dds_user_credentials': self.cred.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_output_dir = JobOutputDir.objects.first()
        self.assertEqual(self.my_job, job_output_dir.job)
        self.assertEqual('results', job_output_dir.dir_name)
        self.assertEqual('123', job_output_dir.project_id)
        self.assertEqual(self.cred, job_output_dir.dds_user_credentials)

    def test_can_use_others_creds(self):
        url = reverse('joboutputdir-list')
        response = self.client.post(url, format='json', data={
            'job': self.my_job.id,
            'dir_name': 'results',
            'project_id': '123',
            'dds_user_credentials': self.others_cred.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_dirs_admin(self):
        # Admin can list other users job-output-directories
        JobOutputDir.objects.create(job=self.my_job, dir_name='results', project_id='1',
                                    dds_user_credentials=self.cred)
        self.user_login.become_admin_user()
        url = reverse('admin_joboutputdir-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        job_output_dir = response.data[0]
        self.assertEqual(self.my_job.id, job_output_dir['job'])
        self.assertEqual('results', job_output_dir['dir_name'])
        self.assertEqual('1', job_output_dir['project_id'])
        self.assertEqual(self.cred.id, job_output_dir['dds_user_credentials'])

    def test_create_admin(self):
        # Admin can create other users job-output-directories
        self.user_login.become_admin_user()
        url = reverse('admin_joboutputdir-list')
        response = self.client.post(url, format='json', data={
            'job': self.my_job.id,
            'dir_name': 'results',
            'project_id': '123',
            'dds_user_credentials': self.cred.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_output_dir = JobOutputDir.objects.first()
        self.assertEqual(self.my_job, job_output_dir.job)
        self.assertEqual('results', job_output_dir.dir_name)
        self.assertEqual('123', job_output_dir.project_id)
        self.assertEqual(self.cred, job_output_dir.dds_user_credentials)


class JobQuestionnaireTestCase(APITestCase):
    def setUp(self):
        """
        Create two questionnaires since this should be a read only endpoint.
        """
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.system_job_order1 = json.dumps({'system_input': 1})
        self.system_job_order2 = json.dumps({'system_input': 2})
        self.flavor = VMFlavor.objects.create(vm_flavor='flavor1')
        self.project = VMProject.objects.create(vm_project_name='bespin-project')
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)
        self.questionnaire1 = JobQuestionnaire.objects.create(name='Workflow1',
                                                              description='A really large workflow',
                                                              workflow_version=self.workflow_version,
                                                              system_job_order=self.system_job_order1,
                                                              vm_flavor = self.flavor,
                                                              vm_project = self.project,

        )
        self.questionnaire2 = JobQuestionnaire.objects.create(name='Workflow2',
                                                              description='A rather small workflow',
                                                              workflow_version=self.workflow_version,
                                                              system_job_order=self.system_job_order2,
                                                              vm_flavor = self.flavor,
                                                              vm_project = self.project,
                                                              )
        self.questionnaire2.save()

    def test_user_can_read(self):
        self.user_login.become_normal_user()
        url = reverse('jobquestionnaire-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))

        url = '{}{}/'.format(reverse('jobquestionnaire-list'), self.questionnaire1.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Workflow1', response.data['name'])
        self.assertEqual('A really large workflow', response.data['description'])
        self.assertEqual(self.workflow_version.id, response.data['workflow_version'])
        self.assertEqual(self.system_job_order1, response.data['system_job_order'])
        self.assertEqual(self.flavor.id, response.data['vm_flavor']['id'])
        self.assertEqual(self.project.id, response.data['vm_project']['id'])

        url = '{}{}/'.format(reverse('jobquestionnaire-list'), self.questionnaire2.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('Workflow2', response.data['name'])
        self.assertEqual('A rather small workflow', response.data['description'])
        self.assertEqual(self.workflow_version.id, response.data['workflow_version'])
        self.assertEqual(self.system_job_order2, response.data['system_job_order'])
        self.assertEqual(self.flavor.id, response.data['vm_flavor']['id'])
        self.assertEqual(self.project.id, response.data['vm_project']['id'])

    def test_user_cant_write(self):
        self.user_login.become_normal_user()
        url = reverse('jobquestionnaire-list')
        response = self.client.post(url, format='json', data={
            'description': 'Workflow3',
            'workflow_version': self.workflow_version.id
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        questionnaire1_endpoint = '{}{}/'.format(url, self.questionnaire1.id)
        response = self.client.put(questionnaire1_endpoint, format='json', data={
            'description': 'Workflow3',
            'workflow_version': self.workflow_version.id
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class JobAnswerSetTests(APITestCase):

    def setUp(self):
        self.user_login = UserLogin(self.client)
        workflow = Workflow.objects.create(name='RnaSeq')
        cwl_url = "https://raw.githubusercontent.com/johnbradley/iMADS-worker/master/predict_service/predict-workflow-packed.cwl"
        self.flavor = VMFlavor.objects.create(vm_flavor='flavor1')
        self.project = VMProject.objects.create(vm_project_name='bespin-project')
        self.system_job_order1 = json.dumps({'system_input': 1})
        self.system_job_order2 = json.dumps({'system_input': 2})
        self.workflow_version = WorkflowVersion.objects.create(workflow=workflow,
                                                               version="1",
                                                               url=cwl_url)
        self.questionnaire1 = JobQuestionnaire.objects.create(description='Workflow1',
                                                              workflow_version=self.workflow_version,
                                                              system_job_order=self.system_job_order1,
                                                              vm_flavor=self.flavor,
                                                              vm_project=self.project,
                                                              )
        self.questionnaire2 = JobQuestionnaire.objects.create(description='Workflow1',
                                                              workflow_version=self.workflow_version,
                                                              system_job_order=self.system_job_order2,
                                                              vm_flavor=self.flavor,
                                                              vm_project=self.project,
                                                              )
        self.other_user = self.user_login.become_other_normal_user()
        self.user = self.user_login.become_normal_user()
        self.endpoint = DDSEndpoint.objects.create(name='DukeDS', agent_key='secret',
                                                   api_root='https://someserver.com/api')
        self.user_job_order1 = json.dumps({'input1': 'value1'})
        self.user_job_order2 = json.dumps({'input1': 'value1', 'input2': [1,2,3]})

    def test_user_crud(self):
        url = reverse('jobanswerset-list')
        response = self.client.post(url, format='json', data={
            'questionnaire': self.questionnaire1.id,
            'job_name': 'Test job 1',
            'user_job_order' : self.user_job_order1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(1, len(JobAnswerSet.objects.all()))
        job_answer_set = JobAnswerSet.objects.first()
        self.assertEqual(job_answer_set.user_job_order, self.user_job_order1)

        url = '{}{}/'.format(reverse('jobanswerset-list'), response.data['id'])
        response = self.client.put(url, format='json', data={
            'questionnaire': self.questionnaire1.id,
            'job_name': 'Test job 2',
            'user_job_order': self.user_job_order2,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job_answer_set = JobAnswerSet.objects.first()
        self.assertEqual(job_answer_set.user_job_order, self.user_job_order2)

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, len(JobAnswerSet.objects.all()))


    def setup_minimal_questionnaire(self):
        # user_cred = DDSUserCredential.objects.create(endpoint=self.endpoint, user=self.user, token='secret2',
        #                                              dds_id='1')
        questionnaire = JobQuestionnaire.objects.create(description='Workflow1',
                                                        workflow_version=self.workflow_version,
                                                        system_job_order=self.system_job_order1,
                                                        vm_flavor=self.flavor,
                                                        vm_project=self.project,
                                                        )
        return questionnaire

    def test_create_job_with_items(self):
        questionnaire = self.setup_minimal_questionnaire()
        url = reverse('jobanswerset-list')
        response = self.client.post(url, format='json', data={
            'questionnaire': questionnaire.id,
            'job_name': 'Test job with items',
            'user_job_order': self.user_job_order1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_answer_set_id = response.data['id']
        url = reverse('jobanswerset-list') + str(job_answer_set_id) + "/create-job/"
        response = self.client.post(url, format='json', data={})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual('Test job with items', response.data['name'])
        self.assertEqual(self.flavor.vm_flavor, response.data['vm_flavor'])
        self.assertEqual(self.project.vm_project_name, response.data['vm_project_name'])
        expected_job_order = json.loads(self.system_job_order1).copy()
        expected_job_order.update(json.loads(self.user_job_order1))
        self.assertEqual(json.dumps(expected_job_order), response.data['job_order'])
        self.assertEqual(1, len(Job.objects.all()))

    def test_user_order_overrides_system_order(self):
        pass

    # TODO: Restore test after creating job output dirs
    # @patch('data.jobfactory.JobOutputDir')
    # def test_create_job_with_exception_rolls_back(self, MockJobOutputDir):
    #     MockJobOutputDir.objects.create.side_effect = ValueError("oops")
    #     self.assertEqual(0, len(Job.objects.all()))
    #     questionnaire = self.setup_minmal_questionnaire()
    #     url = reverse('jobanswerset-list')
    #     response = self.client.post(url, format='json', data={
    #         'questionnaire': questionnaire.id,
    #         'answers': [],
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     job_answer_set_id = response.data['id']
    #     url = reverse('jobanswerset-list') + str(job_answer_set_id) + "/create-job/"
    #     with self.assertRaises(ValueError):
    #         response = self.client.post(url, format='json', data={})
    #     self.assertEqual(0, len(Job.objects.all()))

