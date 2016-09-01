"""
# Recruiter Email

"""
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
    original                = ndb.TextProperty(required=True)

    # Timestamps
    created_at              = ndb.DateTimeProperty(auto_now_add=True)
    updated_at              = ndb.DateTimeProperty(auto_now=True)

    # Class Methods
    @staticmethod
    def from_inbound_handler(message):
        recruitment = RecruiterEmail(forwarder=message.sender,
                                     forwarding_address=message.to,
                                     original=message.original.as_string())
        recruitment.put()
        return recruitment
