"""
# Recruiter Email

## Related Models

- belongs_to Recruiter
"""
import email
from email.utils import parseaddr
import hashlib
from datetime import datetime
import string

from google.appengine.ext import ndb
from google.appengine.api.mail import InboundEmailMessage


#
# Model
#
class RecruiterEmail(ndb.Model):
    #
    # Attrs
    #
    # Forward Email Fields
    forwarder               = ndb.StringProperty(required=True)
    forwarding_address      = ndb.StringProperty(required=True)
    forwarded_subject       = ndb.StringProperty()
    original                = ndb.TextProperty(required=True)
    checksum                = ndb.ComputedProperty(lambda self: self._compute_checksum())

    # Recruitment Fields
    recruiter_name          = ndb.StringProperty()
    recruiter_email         = ndb.StringProperty()
    sent_to                 = ndb.StringProperty()
    subject                 = ndb.StringProperty()
    plain_body              = ndb.TextProperty()
    html_body               = ndb.TextProperty()
    sent_at                 = ndb.DateTimeProperty()
    replied_at              = ndb.DateTimeProperty()

    # Related Models
    recruiter_key           = ndb.KeyProperty(required=False)        # kind=Recruiter

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

    @property
    def recruiter(self):
        if not self.recruiter_key:
            return None
        else:
            return self.recruiter_key.get()

    @property
    def sent_on(self):
        return self.sent_at.date()

    @property
    def replied_to_recruiter(self):
        if not self.replied_at:
            return False
        else:
            return True

    #
    # Class Methods
    #
    @staticmethod
    def from_inbound_handler(message):
        existing_recruitment = RecruiterEmail.get_by_incoming_message(message)

        if existing_recruitment:
            existing_recruitment.already_existed = True
            return existing_recruitment

        recruitment = RecruiterEmail(forwarder=message.sender.strip(),
                                     forwarding_address=message.to.strip(),
                                     forwarded_subject=message.subject.strip(),
                                     original=message.original.as_string().strip())
        recruitment.already_existed = False
        recruitment.extract_recruitment_properties()
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
                    return part.get_payload(decode=True).strip()

        # Not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            return message.get_payload(decode=True).strip()

    @staticmethod
    def from_line_to_name_and_email(from_line):
        # Based on http://stackoverflow.com/a/550036/1093087.
        from_line = from_line.strip()

        if not from_line:
            return None, None

        # Names with commas are supposed to enclosed in quotes, but sometimes they are not!
        # For example: Last, First <flast@example.com>
        if ',' in from_line and '<' in from_line and from_line[-1] == '>':
            name, email = from_line.rsplit('<')
            email = "<%s" % (email)
            name = name.strip()
            if name[0] not in ["'", '"']:
                names = name.split(',')
                name = '"%s"' % (name)
            from_line = '%s %s' % (name, email)

        name, email = parseaddr(from_line)

        if email:
            email = email.strip().lower()

        if email and not name:
            name = email.split('@')[0]

        name = RecruiterEmail.normalize_name(name)

        return name, email

    @staticmethod
    def normalize_name(name):
        if '.' in name:
            name = name.replace('.', ' ')

        # Last, First -> First Last
        while ',' in name:
            names = name.rsplit(',')
            name = '%s %s' % (names[-1], names[0])

        # Try to filter out any crap.
        names = name.split(' ')
        good_names = []
        for name in names:
            name = name.strip()
            if name != '' and name[0] not in string.punctuation:
                good_names.append(name.title())

        return ' '.join(good_names)

    @staticmethod
    def extract_recruitment_data(plain_body):
        extract = {}
        recruiter_headers = ['from', 'date', 'subject', 'to']

        def normalize_date(timestamp):
            gmail_format = '%a, %b %d, %Y at %I:%M %p'
            if not timestamp:
                return None
            else:
                return datetime.strptime(timestamp, gmail_format)

        lines = plain_body.strip().split("\n")

        for line in lines:
            pair = line.split(':', 1)
            if len(pair) < 2:
                continue
            else:
                key, value = pair

            header = key.strip().lower()

            if header in recruiter_headers:
                extract[header] = value.strip()

            if header == 'to':
                break

        name, email = RecruiterEmail.from_line_to_name_and_email(extract.get('from'))

        return {
            'recruiter_name': RecruiterEmail.normalize_name(name),
            'recruiter_email': email,
            'sent_to': extract.get('to'),
            'sent_at': normalize_date(extract.get('date')),
            'subject': extract.get('subject'),
            'plain_body': plain_body.strip()
        }

    #
    # Query Methods
    #
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
    def s_by_recruiter(recruiter, **options):
        limit = options.get('limit', 10)
        return RecruiterEmail.query(RecruiterEmail.recruiter_key == recruiter.key) \
                             .order(-RecruiterEmail.sent_at) \
                             .fetch(limit)

    @staticmethod
    def s_sent_since(cutoff):
        limit = 1000
        return RecruiterEmail.query(RecruiterEmail.sent_at > cutoff) \
                             .order(-RecruiterEmail.sent_at) \
                             .fetch(limit)

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

    #
    # Public Methods
    #
    def delete(self):
        recruiter = self.recruiter

        if recruiter:
            recruiter = recruiter.decrement_email_count()

        self.key.delete()
        return recruiter

    def sync_with_recruiter(self, recruiter):
        self.recruiter_name = recruiter.name
        self.recruiter_email = recruiter.email
        self.put()
        return self

    def extract_recruitment_properties(self):
        mime_message = email.message_from_string(self.original)
        inbound_message = InboundEmailMessage(mime_message)

        # Extract plain and html body.
        self.plain_body = list(inbound_message.bodies('text/plain'))[0][1].decode().strip()
        self.html_body = list(inbound_message.bodies('text/html'))[0][1].decode().strip()

        # Extract recruitment data from plain text body.
        data = RecruiterEmail.extract_recruitment_data(self.plain_body)

        # Set recruitment fields.
        self.subject = data.get('subject')
        self.recruiter_name = data.get('recruiter_name')
        self.recruiter_email = data.get('recruiter_email')
        self.sent_to = data.get('sent_to')
        self.sent_at = data.get('sent_at')

        return self

    def associate_recruiter(self, recruiter):
        if not recruiter:
            return self

        self.recruiter_key = recruiter.key
        recruiter.increment_email_count()
        self.put()
        return self

    #
    # Private Methods
    #
    def _compute_checksum(self):
        body = RecruiterEmail.extract_plaintext_body(self.original)
        return hashlib.md5(body).hexdigest()
