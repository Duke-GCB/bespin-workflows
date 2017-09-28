from django.test import TestCase
from mailer import EmailMessageFactory, EmailMessageSender, JobMailer
from models import EmailMessage, EmailTemplate, Job
from mock import MagicMock, patch, call
from exceptions import EmailException

class EmailMessageFactoryTestCase(TestCase):

    def setUp(self):
        self.email_template = EmailTemplate.objects.create(
            name='template1',
            body_template='Body {{ field1 }}',
            subject_template='Subject {{ field2}}',
        )
        self.context = {
            'field1': 'abc',
            'field2': 'def'
        }
        self.sender_email = 'sender@example.com'
        self.to_email = 'recipient@university.edu'

    def test_makes_message(self):
        factory = EmailMessageFactory(self.email_template)

        message = factory.make_message(
            self.context,
            self.sender_email,
            self.to_email
        )

        self.assertEqual(message.body, 'Body abc')
        self.assertEqual(message.subject, 'Subject def')
        self.assertEqual(message.sender_email, self.sender_email)
        self.assertEqual(message.to_email, self.to_email)


class EmailMessageSenderTestCase(TestCase):

    def setUp(self):
        self.subject = 'Message Subject'
        self.body = 'Message Body'
        self.sender_email = 'sender@example.com'
        self.to_email = 'recipient@university.edu'

        self.email_message = EmailMessage.objects.create(
            body=self.body,
            subject=self.subject,
            sender_email=self.sender_email,
            to_email=self.to_email
        )

    @patch('data.mailer.DjangoEmailMessage')
    def test_sends_email(self, MockDjangoEmailMessage):
        mock_send = MagicMock()
        MockDjangoEmailMessage.return_value.send = mock_send
        sender = EmailMessageSender(self.email_message)
        sender.send()
        self.assertEqual(self.email_message.state, EmailMessage.MESSAGE_STATE_SENT)
        self.assertEqual(mock_send.call_count, 1)
        self.assertTrue(mock_send.call_args(self.subject, self.body, self.sender_email, [self.to_email],))

    @patch('data.mailer.DjangoEmailMessage')
    def test_captures_errors_on_send(self, MockDjangoEmailMessage):
        mock_send = MagicMock()
        mock_send.side_effect = Exception('Email error')
        MockDjangoEmailMessage.return_value.send = mock_send
        sender = EmailMessageSender(self.email_message)
        with self.assertRaises(EmailException):
            sender.send()
        self.assertEqual(self.email_message.state, EmailMessage.MESSAGE_STATE_ERROR)
        self.assertEqual(self.email_message.errors, 'Email error')
        self.assertEqual(mock_send.call_count, 1)
        self.assertTrue(mock_send.call_args(self.subject, self.body, self.sender_email, [self.to_email],))


class JobMailerTestCase(TestCase):
    def setUp(self):
        EmailTemplate.objects.create(
            name='job-running-user',
            body_template='Started {{ name }}',
            subject_template ='Job {{ id }} has started'
        )
        EmailTemplate.objects.create(
            name='job-cancel-user',
            body_template='Canceled {{ name }}',
            subject_template ='Job {{ id }} has been canceled'
        )
        EmailTemplate.objects.create(
            name='job-finished-user',
            body_template='Finished {{ name }}',
            subject_template ='Job {{ id }} has completed'
        )
        EmailTemplate.objects.create(
            name='job-finished-sharegroup',
            body_template='Share Group: Finished {{ name }}',
            subject_template ='Share Group: Job {{ id }} has completed'
        )
        EmailTemplate.objects.create(
            name='job-error-user',
            body_template='Errored {{ name }}',
            subject_template ='Job {{ id }} has failed'
        )

    @patch('data.mailer.DjangoEmailMessage')
    def test_mails_running_job(self, MockSender):
        mock_send = MagicMock()
        MockSender.return_value.send = mock_send
        expected_body = 'Started TEST'
        expected_subject = 'Job 56 has started'
        expected_to_email = 'user@domain.com'
        expected_sender_email = 'sender@otherdomain.com'
        user = MagicMock(email=expected_to_email)
        job = MagicMock(state=Job.JOB_STATE_RUNNING, id=56, user=user)
        job.name = 'TEST'
        mailer = JobMailer(job,sender_email=expected_sender_email)
        mailer.mail_current_state()
        self.assertTrue(MockSender.called)
        self.assertEqual(mock_send.call_count, 1)
        expected_calls = [
            call(expected_subject, expected_body, expected_sender_email, [expected_to_email]),
            call().send()
        ]
        self.assertEqual(MockSender.mock_calls, expected_calls)

    @patch('data.mailer.DjangoEmailMessage')
    def test_mails_canceled_job(self, MockSender):
        mock_send = MagicMock()
        MockSender.return_value.send = mock_send
        expected_body = 'Canceled TEST'
        expected_subject = 'Job 33 has been canceled'
        expected_to_email = 'user@domain.com'
        expected_sender_email = 'sender@otherdomain.com'
        user = MagicMock(email=expected_to_email)
        job = MagicMock(state=Job.JOB_STATE_CANCEL, id=33, user=user)
        job.name = 'TEST'
        mailer = JobMailer(job,sender_email=expected_sender_email)
        mailer.mail_current_state()
        self.assertTrue(MockSender.called)
        self.assertEqual(mock_send.call_count, 1)
        expected_calls = [
            call(expected_subject, expected_body, expected_sender_email, [expected_to_email]),
            call().send()
        ]
        self.assertEqual(MockSender.mock_calls, expected_calls)

    @patch('data.mailer.DjangoEmailMessage')
    def test_mails_finished_job(self, MockSender):
        mock_send = MagicMock()
        MockSender.return_value.send = mock_send
        expected_user_body = 'Finished TEST'
        expected_user_subject = 'Job 66 has completed'
        expected_sharegroup_body = 'Share Group: Finished TEST'
        expected_sharegroup_subject = 'Share Group: Job 66 has completed'
        expected_user_email = 'user@domain.com'
        expected_sharegroup_email = 'sharegroup@domain.com'
        expected_sender_email = 'sender@otherdomain.com'
        user = MagicMock(email=expected_user_email)
        sharegroup = MagicMock(email=expected_sharegroup_email)
        job = MagicMock(state=Job.JOB_STATE_FINISHED, id=66, user=user, share_group=sharegroup)
        job.name = 'TEST'
        mailer = JobMailer(job,sender_email=expected_sender_email)
        mailer.mail_current_state()
        self.assertTrue(MockSender.called)
        self.assertEqual(mock_send.call_count, 2)
        expected_calls = [
            call(expected_user_subject, expected_user_body, expected_sender_email, [expected_user_email]),
            call().send(),
            call(expected_sharegroup_subject, expected_sharegroup_body, expected_sender_email, [expected_sharegroup_email]),
            call().send(),
        ]
        self.assertEqual(MockSender.mock_calls, expected_calls)

    @patch('data.mailer.DjangoEmailMessage')
    def test_mails_errored_job(self, MockSender):
        mock_send = MagicMock()
        MockSender.return_value.send = mock_send
        expected_body = 'Errored TEST'
        expected_subject = 'Job 61 has failed'
        expected_to_email = 'user@domain.com'
        expected_sender_email = 'sender@otherdomain.com'
        user = MagicMock(email=expected_to_email)
        job = MagicMock(state=Job.JOB_STATE_ERROR, id=61, user=user)
        job.name = 'TEST'
        mailer = JobMailer(job,sender_email=expected_sender_email)
        mailer.mail_current_state()
        self.assertTrue(MockSender.called)
        self.assertEqual(mock_send.call_count, 1)
        expected_calls = [
            call(expected_subject, expected_body, expected_sender_email, [expected_to_email]),
            call().send()
        ]
        self.assertEqual(MockSender.mock_calls, expected_calls)
