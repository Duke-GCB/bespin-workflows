from django.core.mail import EmailMessage as DjangoEmailMessage
from django.template import Template, Context
from django.utils.safestring import mark_safe
from models import Job, EmailMessage, EmailTemplate
from exceptions import EmailException

JOB_MAILER_DEFAULT_EMAIL = 'bespin-service@duke.edu'

class EmailMessageFactory(object):

    def __init__(self, email_template):
        self.email_template = email_template

    @classmethod
    def _render(cls, template, context):
        for k in context:
            context[k] = mark_safe(context[k])
        django_template = Template(template)
        return django_template.render(Context(context))

    def _render_subject(self, context):
        return self._render(self.email_template.subject_template, context)

    def _render_body(self, context):
        return self._render(self.email_template.body_template, context)

    def make_message(self, context, sender_email, to_email):
        body = self._render_body(context)
        subject = self._render_subject(context)
        message = EmailMessage.objects.create(
            body=body,
            subject=subject,
            sender_email=sender_email,
            to_email=to_email,
        )
        return message


class EmailMessageSender(object):

    def __init__(self, email_message):
        self.email_message = email_message

    def send(self):
        django_message = DjangoEmailMessage(
            self.email_message.subject,
            self.email_message.body,
            self.email_message.sender_email,
            [self.email_message.to_email]
        )
        try:
            django_message.send()
            self.email_message.mark_sent()
        except Exception as e:
            self.email_message.mark_error(str(e))
            raise EmailException(e)


class JobMailer(object):

    def __init__(self, job, queue_messages=False, sender_email=JOB_MAILER_DEFAULT_EMAIL):
        self.job = job
        self.sender_email = sender_email
        self.queue_messages = queue_messages

    def _deliver(self, message):
        if self.queue_messages:
            raise NotImplementedError('Queuing not yet implemented')
        else:
            sender = EmailMessageSender(message)
            sender.send()

    def _make_context(self):
        return {
            'id': self.job.id,
            'name': self.job.name,
        }

    def _make_message(self, template_name, to_email):
        context = self._make_context()
        template = EmailTemplate.objects.get(name=template_name)
        factory = EmailMessageFactory(template)
        return factory.make_message(context, self.sender_email, to_email)

    def mail_current_state(self):
        messages = []
        state = self.job.state
        if state == Job.JOB_STATE_RUNNING:
            messages.append(self._make_message('job-running-user', self.job.user.email))
        elif state == Job.JOB_STATE_CANCEL:
            messages.append(self._make_message('job-cancel-user', self.job.user.email))
        elif state == Job.JOB_STATE_FINISHED:
            messages.append(self._make_message('job-finished-user', self.job.user.email))
            messages.append(self._make_message('job-finished-sharegroup', self.job.share_group.email))
        elif state == Job.JOB_STATE_ERROR:
            messages.append(self._make_message('job-error-user', self.job.user.email))
        for message in messages:
            self._deliver(message)
