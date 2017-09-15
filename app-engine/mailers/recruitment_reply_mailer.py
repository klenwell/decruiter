import logging
from datetime import datetime
from google.appengine.api import mail
from models.recruiter_email import RecruiterEmail
from flask import render_template
from controllers import app
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
        self.recruitment_id = recruitment.public_id

    def generate_subject(self, recruitment):
        subject_f = 'Thanks for contacting me on %s about developer position'
        return subject_f % (recruitment.sent_on)

    def generate_body(self, recruitment):
        return render_template('emails/recruitment_reply.txt',
                               recruitment=recruitment,
                               secrets=secrets)

    def deliver(self):
        recruitment = RecruiterEmail.read(self.recruitment_id)
        sender = secrets.AUTHORIZED_APP_ENGINE_SENDER
        recipient = recruitment.recruiter.email

        # Already replied?
        if recruitment.replied_to_recruiter:
            log_f = 'Automated reply not delivered: already sent to recruiter %s at %s.'
            logging.info(log_f % (recruitment.recruiter.email, recruitment.replied_at))
            return False

        # Uncomment for live testing.
        #recipient = secrets.AUTHORIZED_FORWARDERS[1]

        # Required to avoid AttributeError.
        # See: https://stackoverflow.com/a/31156117/1093087
        with app.app_context():
            mail.send_mail(sender=sender,
                           to=recipient,
                           subject=self.generate_subject(recruitment),
                           body=self.generate_body(recruitment))

        recruitment.replied_at = datetime.now()
        recruitment.put()

        logging.info('Automated reply to recruiter %s sent.' % recruitment.recruiter.email)
        return True
