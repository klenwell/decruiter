from google.appengine.api import mail
from flask import render_template
from config import secrets


class RecruitmentReplyMailer(object):
    #
    # Class Methods
    #
    @staticmethod
    def queue_for_delivery(recruitment):
        mailer = Mailer(recruitment)
        # TODO: Queue

    def __init__(self, recruitment):
        self.sender = secrets.AUTHORIZED_APP_ENGINE_SENDER
        self.recipient = recruitment.recruiter.email
        self.subject = self.generate_subject(recruitment)
        self.body = self.generate_body(recruitment)

    def generate_subject(self, recruitment):
        subject_f = 'Thanks for contacting me on %s about developer position'
        return subject_f % (recruitment.sent_on)

    def generate_body(self, recruitment):
        return render_template('emails/recruitment_reply.txt',
                               recruitment=recruitment,
                               secrets=secrets)

    def deliver(self):
        mail.send_mail(sender=self.sender,
                       to=self.recipient,
                       subject=self.subject,
                       body=self.body)
