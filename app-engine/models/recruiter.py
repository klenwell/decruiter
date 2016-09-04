"""
# Recruiter

## Related Models

- has_many RecruiterEmail
"""
from google.appengine.ext import ndb


#
# Model
#
class Recruiter(ndb.Model):
    #
    # Attrs
    #
    email                   = ndb.StringProperty(required=True)
    name                    = ndb.StringProperty()
    email_count             = ndb.IntegerProperty()

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
        return Recruiter.query(Recruiter.email == email).get()
