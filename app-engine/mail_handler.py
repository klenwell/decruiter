"""
# Mail Handler

Source
- https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/standard/mail/handle_incoming_email.py
"""
import logging
import webapp2
from email.utils import parseaddr

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter
from mailers.recruitment_reply_mailer import RecruitmentReplyMailer

from config.secrets import AUTHORIZED_FORWARDERS, AUTOMATED_REPLY_TRIGGER_EMAIL


class HandlerAuthorizationError(Exception): pass


class RecruiterEmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Message to %s from %s with subject: %s" % (mail_message.to,
                                                                 mail_message.sender,
                                                                 mail_message.subject))

        # Extract forwarder and recipient email addresses
        _, forwarder_email = parseaddr(mail_message.sender)
        _, recipient_email = parseaddr(mail_message.to)

        # Authenticate email forwarder.
        if forwarder_email in AUTHORIZED_FORWARDERS:
            msg = '%s is authorized to forward recruitments.' % (forwarder_email)
            logging.debug(msg)
        else:
            msg = '%s is not authorized to forward recruitments.' % (forwarder_email)
            raise HandlerAuthorizationError(msg)

        # Parse and store recruitment.
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Associate recruiter and log result.
        if recruitment.already_existed:
            log_f = 'Recruitment "%s" from %s already existed.'
        else:
            log_f = 'Recruitment "%s" from %s saved.'
            recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
            recruitment.associate_recruiter(recruiter)
        logging.info(log_f % (recruitment.subject, recruitment.recruiter.email))

        # Email recruiter.
        if recipient_email == AUTOMATED_REPLY_TRIGGER_EMAIL:
            mailer = RecruitmentReplyMailer(recruitment)
            mailer.deliver()
        else:
            logging.info('Automated reply not sent to recruiter %s.' % (recruitment.recruiter.email))


app = webapp2.WSGIApplication([RecruiterEmailHandler.mapping()], debug=True)
