Sign App
==========

Flow
----

1. user with permission sends doc for signing
2. claim_url : user sets up the doc to sign placing signatures and indicatign when ready
3. invited signers recieve email (from Hellosign not us) to come and sign the document
4. signers sign document - sends webhook back to us which processes the event
5. once all signers are complete (takes a few minutes) then Hellosign sends an 'signature_request_all_signed'
6. we run async the _download_signing_complete_document; which then downloads the signed copy and makes it final (is_executed = True)

Dependencies
------------

We are VERY dependent on HelloSign webhooks here, they have a pretty bad api and in some cases
we are simply not able to get the signatures data. (@TODO need to investigate the cases that will happen
when a webhook fails for whatever reason)

1. -e git+https://github.com/rosscdh/django-hello_sign.git#egg=django-hello_sign - Django wrapper provides signals and webooks as well as services to talk with HS
2. -e git+https://github.com/rosscdh/hellosign.git#egg=hellosign - original python lib that provides missing functionality (was missing at time of writing) such as downloadfinalcopy etc
3. hellosign-python-sdk - HS provided sdk was released in may 2014 with many many problems


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
