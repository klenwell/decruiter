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

from config.secrets import AUTHORIZED_FORWARDERS, AUTOMATED_REPLY_TRIGGER_EMAIL


class HandlerAuthorizationError(Exception): pass


class RecruiterEmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Message to %s from %s with subject: %s" % (mail_message.to,
                                                                 mail_message.sender,
                                                                 mail_message.subject))

        # Authenticate email forwarder.
        _, forwarder = parseaddr(mail_message.sender)
        if forwarder in AUTHORIZED_FORWARDERS:
            msg = '%s is authorized to forward recruitments.' % (forwarder)
            logging.debug(msg)
        else:
            msg = '%s is not authorized to forward recruitments.' % (forwarder)
            raise HandlerAuthorizationError(msg)

        # Parse and store recruitment.
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Associate recruiter and log result.
        if recruitment.already_existed:
            msg_f = 'Recruitment "%s" from %s already existed.'
        else:
            msg_f = 'Recruitment "%s" from %s saved.'
            recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
            recruitment.associate_recruiter(recruiter)
        logging.info(msg_f % (recruitment.subject, recruitment.recruiter.email))

        # Email recruiter.
        if mail_message.to == AUTOMATED_REPLY_EMAIL:
            msg_f = 'Automated reply sent to recruiter %s.'
            # Generate and send email.
        else:
            msg_f = 'Automated reply not sent to recruiter %s.'
        logging.info(msg_f % (recruitment.recruiter.email))


app = webapp2.WSGIApplication([RecruiterEmailHandler.mapping()], debug=True)
