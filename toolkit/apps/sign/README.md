Sign App
==========

As a lawyer

Once a item has been marked as final, I want to invite another person 
(full name, email) to sign that specific revision and execute the document.

Provide a means to invite a current user, or create a new user based on email
to sign a document at a unique to that user+document-revision url.

Dependencies
------------

1. https://github.com/rosscdh/django-hello_sign


Models
------

A model to link a "final" attachment.revision object with a user object.
slug should be a GUID.


Views
-----

__sign__

1. view to provide signer with access to the hellosign url for a document
2. should provide basic info about the lawyer, client, client-user and the 
document being signed as well as display the hellosign interface


Signals
-------

1. listen for django-hello_sign module events and generate activity stream for each
type of event listend for hello_sign.signals.hellosign_webhook_event_recieved
2. create activity stream entries for the matter.item.revision being reviewed.
