from django.test import TestCase
from data.util import has_download_permissions, DataServiceError, WrappedDataServiceException, get_workflow_version_info
from unittest.mock import patch, Mock, call

class HasDownloadPermissionsTestCase(TestCase):
    @patch('data.util.get_dds_config_for_credentials')
    @patch('data.util.RemoteStore')
    def test_has_download_permissions_user_already_has_permissions(self, mock_remote_store, mock_get_dds_config):
        dds_user_credential = Mock()
        project_id = '123'
        mock_remote_store.return_value.data_service.get_user_project_permission.return_value.json.return_value = {
            'auth_role': {
                'id': 'file_downloader'
            }
        }
        self.assertTrue(has_download_permissions(dds_user_credential, project_id))
        mock_remote_store.return_value.data_service.get_user_project_permission.return_value.json.return_value = {
            'auth_role': {
                'id': 'file_downloader'
            }
        }
        self.assertTrue(has_download_permissions(dds_user_credential, project_id))
        mock_remote_store.return_value.data_service.get_user_project_permission.return_value.json.return_value = {
            'auth_role': {
                'id': 'file_editor'
            }
        }
        self.assertTrue(has_download_permissions(dds_user_credential, project_id))
        mock_remote_store.return_value.data_service.get_user_project_permission.return_value.json.return_value = {
            'auth_role': {
                'id': 'project_admin'
            }
        }
        self.assertTrue(has_download_permissions(dds_user_credential, project_id))

    @patch('data.util.get_dds_config_for_credentials')
    @patch('data.util.RemoteStore')
    def test_has_download_permissions_user_wrong_permissions(self, mock_remote_store, mock_get_dds_config):
        dds_user_credential = Mock()
        project_id = '123'
        mock_remote_store.return_value.data_service.get_user_project_permission.return_value.json.return_value = {
            'auth_role': {
                'id': 'project_metadata_viewer'
            }
        }
        self.assertFalse(has_download_permissions(dds_user_credential, project_id))

    @patch('data.util.get_dds_config_for_credentials')
    @patch('data.util.RemoteStore')
    def test_has_download_permissions_user_no_permissions(self, mock_remote_store, mock_get_dds_config):
        dds_user_credential = Mock()
        project_id = '123'
        data_service_error = DataServiceError(response=Mock(status_code=404), url_suffix=Mock(), request_data=Mock())
        mock_remote_store.return_value.data_service.get_user_project_permission.side_effect = data_service_error
        self.assertFalse(has_download_permissions(dds_user_credential, project_id))

    @patch('data.util.get_dds_config_for_credentials')
    @patch('data.util.RemoteStore')
    def test_has_download_permissions_unexpected_error(self, mock_remote_store, mock_get_dds_config):
        dds_user_credential = Mock()
        project_id = '123'
        data_service_error = DataServiceError(response=Mock(status_code=500), url_suffix=Mock(), request_data=Mock())
        mock_remote_store.return_value.data_service.get_user_project_permission.side_effect = data_service_error
        with self.assertRaises(WrappedDataServiceException):
            self.assertFalse(has_download_permissions(dds_user_credential, project_id))


@patch('data.util.requests')
class GetWorkflowVersionInfoTestCase(TestCase):

    def test_get_url(self, mock_requests):
        mock_content = Mock()
        mock_get = mock_requests.get
        mock_response = mock_get.return_value
        mock_decode = mock_response.content.decode
        mock_decode.return_value = mock_content
        mock_encoding = Mock()
        mock_response.encoding = mock_encoding
        mock_response.headers = {'Content-Type': 'text/plain'}
        version_info_url = 'https://example.org/info'
        mock_workflow_version = Mock(version_info_url=version_info_url)
        version_info = get_workflow_version_info(mock_workflow_version)

        self.assertEqual(mock_get.call_args, call(version_info_url), 'calls requests.get with the version_info_url')
        self.assertEqual(mock_decode.call_args, call(mock_encoding), 'calls decode with response.encoding')
        self.assertEqual(version_info, {
            'workflow_version': mock_workflow_version,
            'content': mock_content,
            'content_type': 'text/plain',
            'url': version_info_url
        })

    def test_raises_on_response_status(self, mock_requests):
        mock_response = mock_requests.get.return_value
        mock_response .raise_for_status.side_effect = Exception('raise_for_status')
        with self.assertRaises(Exception):
            get_workflow_version_info(Mock())
