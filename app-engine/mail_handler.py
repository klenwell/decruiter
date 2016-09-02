"""
# Mail Handler

Source
- https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/standard/mail/handle_incoming_email.py
"""
import logging
import webapp2

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

from models.recruiter_email import RecruiterEmail


class RecruiterEmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Message to %s from %s with subject: %s" % (mail_message.to,
                                                                 mail_message.sender,
                                                                 mail_message.subject))

        recruitment = RecruiterEmail.from_handler(mail_message)

        if recruiter.already_existed:
            logging.info('Recruitment already existed: %s' % (recruitment))
        else:
            logging.info('Recruitment saved: %s' % (recruitment))

app = webapp2.WSGIApplication([RecruiterEmailHandler.mapping()], debug=True)