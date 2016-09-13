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

from config.secrets import AUTHORIZED_FORWARDERS


class HandlerAuthorizationError(Exception): pass


class RecruiterEmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Message to %s from %s with subject: %s" % (mail_message.to,
                                                                 mail_message.sender,
                                                                 mail_message.subject))

        # Authenticate email forwarder.
        _, forwarder = parseaddr(mail_message.sender)
        if forwarder not in AUTHORIZED_FORWARDERS:
            msg = '%s is not authorized to forward recruitments' % (forwarder)
            raise HandlerAuthorizationError(msg)

        # Parse and store recruitment.
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Log result.
        if recruitment.already_existed:
            f = 'Recruitment "%s" from %s already existed.'
            logging.info(f % (recruitment.subject, recruitment.recruiter.email))
        else:
            recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
            recruitment.associate_recruiter(recruiter)
            f = 'Recruitment "%s" from %s saved.'
            logging.info(f % (recruitment.subject, recruitment.recruiter.email))


app = webapp2.WSGIApplication([RecruiterEmailHandler.mapping()], debug=True)
