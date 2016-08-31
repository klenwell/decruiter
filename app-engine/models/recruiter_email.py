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
    raw                     = ndb.TextProperty(required=True)

    # Timestamps
    created_at              = ndb.DateTimeProperty(auto_now_add=True)
    updated_at              = ndb.DateTimeProperty(auto_now=True)
