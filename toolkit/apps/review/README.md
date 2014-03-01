Review App
==========

As a lawyer or customer

I want to invite another person (full name, email) to review a document revision
in order to gain feedback and or another version of the document.

Provide a means to invite a current user, or create a new user based on email
to review a document at a unique to that user+document-revision url.


Dependencies
------------

1. https://github.com/rosscdh/django-crocdoc (pending)


Models
------

A model to link an attachment.revision object with a user object.
slug should be a GUID


Views
-----

__review__

1. view to provide reviewer with access to the crocdoc url for a document
2. should provide basic info about the lawyer, client, client-user and the 
document being reviewed


Signals
-------

1. listen for django-crocdoc module events and generate activity stream for each
type of event

