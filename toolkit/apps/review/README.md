Review App
==========

As a lawyer or customer

I want to invite another person (full name, email) to review a document revision
in order to gain feedback and or another version of the document.

Provide a means to invite a current user, or create a new user based on email
to review a document at a unique to that user+document-revision url.


Dependencies
------------

1. https://github.com/rosscdh/django-crocdoc


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
3. matter participants automatically get a review_document to interact and comment on alongside the other participants
4. matter participants can also be invited to review a document; in this case they should be shown the url of the primary review_document

![item reviews overview](https://s3-eu-west-1.amazonaws.com/documentation-lawpal/item_latest_revision_reviews_overview.png?cache=2 "Item Document Reviews Overview")


Signals
-------

1. listen for django-crocdoc module events and generate activity stream for each
type of event
2. create activity stream entries for the matter.item.revision being reviewed.


Technical
---------

1. an item by default has a ReviewDocument object that all of 
the matter.participants have access to. This is to allow the participants to
interact with each other but noone else

2. an item.revision gets a ReviewDocument per reviwer (who is invited to review the doc)
The purpose of doing it in this way is to ensure that the reviewer is never exposed
to any of the conversation that happens between lawyer and participants at the matter level

3. in addition the item.revision ReviewDocument object must also include the matter.participants
The purpose of this is to allow the higher level participants to partake in communication with
that invited reviewer

4. comments from all ReviewDocument objects are stored against the matter.item in the activity stream
