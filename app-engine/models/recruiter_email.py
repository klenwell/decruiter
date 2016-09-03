"""
# Recruiter Email

"""
import email
import hashlib

from google.appengine.ext import ndb


#
# Model
#
class RecruiterEmail(ndb.Model):
    #
    # Attrs
    #
    # Fields
    forwarder               = ndb.StringProperty(required=True)
    forwarding_address      = ndb.StringProperty(required=True)
    forwarded_subject       = ndb.StringProperty()
    original                = ndb.TextProperty(required=True)
    checksum                = ndb.ComputedProperty(lambda self: self._compute_checksum())

    # Timestamps
    created_at              = ndb.DateTimeProperty(auto_now_add=True)
    updated_at              = ndb.DateTimeProperty(auto_now=True)

    # Virtual Fields
    @property
    def public_id(self):
        if not self.key:
            return None
        else:
            return self.key.id()

    @property
    def original_length(self):
        return len(self.original)

    # Class Methods
    @staticmethod
    def from_inbound_handler(message):
        existing_recruitment = RecruiterEmail.get_by_incoming_message(message)

        if existing_recruitment:
            existing_recruitment.already_existed = True
            return existing_recruitment

        recruitment = RecruiterEmail(forwarder=message.sender,
                                     forwarding_address=message.to,
                                     forwarded_subject=message.subject,
                                     original=message.original.as_string())
        recruitment.already_existed = False
        recruitment.put()
        return recruitment

    @staticmethod
    def extract_plaintext_body(raw_email_str):
        # See http://stackoverflow.com/a/32840516/1093087
        message = email.message_from_string(raw_email_str)

        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                disposition = str(part.get('Content-Disposition'))

                # Skip any text/plain (txt) attachments
                if content_type == 'text/plain' and 'attachment' not in disposition:
                    return part.get_payload(decode=True)

        # Not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            return message.get_payload(decode=True)

    # Query Methods
    @staticmethod
    def read(public_id):
        if not public_id:
            return None

        return ndb.Key('RecruiterEmail', int(public_id)).get()

    @staticmethod
    def s_recently_received(**options):
        limit = options.get('limit', 25)
        return RecruiterEmail.query().order(-RecruiterEmail.created_at).fetch(limit)

    @staticmethod
    def get_by_incoming_message(message):
        original = message.original.as_string()
        body = RecruiterEmail.extract_plaintext_body(original)

        if not body:
            return None

        checksum = hashlib.md5(body).hexdigest()
        return RecruiterEmail.get_by_checksum(checksum)

    @staticmethod
    def get_by_checksum(checksum):
        return RecruiterEmail.query(RecruiterEmail.checksum == checksum).get()

    # Private Methods
    def _compute_checksum(self):
        body = RecruiterEmail.extract_plaintext_body(self.original)
        return hashlib.md5(body).hexdigest()
