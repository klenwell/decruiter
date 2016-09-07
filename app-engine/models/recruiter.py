"""
# Recruiter

## Related Models

- has_many RecruiterEmail
"""
from google.appengine.ext import ndb

from models.recruiter_email import RecruiterEmail


#
# Model
#
class Recruiter(ndb.Model):
    #
    # Attrs
    #
    email                   = ndb.StringProperty(required=True)
    name                    = ndb.StringProperty()
    email_count             = ndb.IntegerProperty(default=0)

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
    def recruitments(self):
        return RecruiterEmail.s_by_recruiter(self, limit=10)

    #
    # Query Methods
    #
    @staticmethod
    def read(public_id):
        if not public_id:
            return None

        return ndb.Key('Recruiter', int(public_id)).get()

    @staticmethod
    def get_by_email(email):
        if not email:
            return None
        else:
            return Recruiter.query(Recruiter.email == email).get()

    @staticmethod
    def get_or_insert_by_recruitment(recruitment):
        recruiter = Recruiter.get_by_email(recruitment.recruiter_email)

        if recruiter:
            return recruiter
        else:
            recruiter = Recruiter(name=recruitment.recruiter_name,
                                  email=recruitment.recruiter_email)
            recruiter.put()
            return recruiter

    @staticmethod
    def s_recently_created(**options):
        limit = options.get('limit', 25)
        return Recruiter.query().order(-Recruiter.created_at).fetch(limit)

    #
    # Public Methods
    #
    def increment_email_count(self):
        self.email_count += 1
        self.put()
        return self

    def decrement_email_count(self):
        self.email_count -= 1
        self.put()
        return self
