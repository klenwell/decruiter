"""
# Recruiter

## Related Models

- has_many RecruiterEmail
"""
import ndbpager
from google.appengine.ext import ndb
from models.recruiter_email import RecruiterEmail


#
# Recruiters can belong to one of the following mailing lists.
#
MAILING_LISTS = ['online', 'local']


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
    mailing_list            = ndb.StringProperty(choices=MAILING_LISTS)

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
        limit=1000
        return RecruiterEmail.s_by_recruiter(self, limit=limit)

    @property
    def mailing_lists(self):
        return MAILING_LISTS

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

    @staticmethod
    def s_paginated(**options):
        page_number = options.get('page_number')
        order_by = options.get('order_by', -Recruiter.created_at)
        limit = options.get('limit', 25)
        query = Recruiter.query().order(order_by)
        return ndbpager.Pager(query=query, page=page_number)

    #
    # Public Methods
    #
    def update(self, **fields):
        # Normalize mailing list
        mailing_list = fields.get('mailing_list')
        if mailing_list == 'none':
            mailing_list = None

        self.name = fields.get('name', self.name)
        self.email = fields.get('email', self.email)
        self.mailing_list = mailing_list

        # Save
        self.put()

        for recruitment in self.recruitments:
            recruitment.sync_with_recruiter(self)

        return self

    def increment_email_count(self):
        self.email_count += 1
        self.put()
        return self

    def decrement_email_count(self):
        self.email_count -= 1
        self.put()
        return self
