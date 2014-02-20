LawPal Toolkit API
------------------


The toolkit api probides a REST (HATEOAS) interface to various aspects of our application
model and workflow application.


What is HATEOAS
===============

1. https://en.wikipedia.org/wiki/HATEOAS
2. http://www.infoq.com/articles/webber-rest-workflow

With this in mind we have built a Marker Object which is a representation of
a Finite-state-machine which represents various workflows within the system.

In otherwords; alongside the normal REST style interface; for each applicable
object, we provide a FSM obejct which will provide the "next" url as well as a
representation of the current state of the requested object.


Authentication
==============

We use basic django session authentication as well as JSON Web Tokens

For more info on JWT read:

http://blog.auth0.com/2014/01/07/angularjs-authentication-with-cookies-vs-token/


Endpoint Overview
=================

__ prefix: /api/v2/ __

Account
=======

As an authenticated user
I need to be able to update my account info
so that I can change my password and email and various details

/account/ (GET,PATCH)
    Allow the [lawyer,customer] user to modify various aspects of their account; automatically
    patches only their account based on session.


Client
======

As a lawyer user
I need to be able to create and modify my list of clients
So that I can create matters for them

/clients/ (GET,POST)
    Allow the [lawyer] user to list and create client objects

/clients/:slug/ (GET,PATCH,DELETE)
    Allow the [lawyer] user to list, update and delete client objects


Matters (Checklist)
===================

As a lawyer or customer user
I need to be able to interact with my matter
In order to provide feedback and initiate workflows

/matters/ (GET,POST)
    Allow the [lawyer] user to list, and create new matter ("workspace") objects


/matters/:slug/ (GET,PATCH,DELETE)
    Allow the [lawyer] user to list, and update an existing matter ("workspace") object


/matters/:slug/items/ (GET,POST)
    Allow the [lawyer,customer] user to list, and create matter items


/matters/:slug/activity/ (GET,POST) - these are created within the system and as part of the system flows
    Allow the [lawyer,customer] user to list activity related to a matter
    POST allows the angular service to send events that are then processed as activity stream items
    @TODO define the params


/matters/:slug/todo/ (GET) - a compiled set of items assigned to the viewing user
    Allow [lawyer,customer] user to list todo items within a matter


/matters/:slug/closing_groups/ (GET)
    Allow [lawyer] user to list items in designated closing groups

/matters/:slug/closing_groups/:name/ (GET)
    Allow [lawyer] user to list items in a specific closing group


Matter Items
============

/matters/:slug/items/ (GET)
    Allow the [lawyer,customer] user to list items that belong to them

/matters/:slug/items/:slug/ (GET,PATCH,DELETE)
    Allow the [lawyer,customer] user to list, and update an existing item
    objects; that belong to them

/matters/:slug/items/:slug/attachments/ (GET) - returns only the most RECENT revision
    Allow [lawyer,customer] user to list and create attachment objects for item objects

/matters/:slug/items/ (GET)
/matters/:slug/items/:slug/ (GET,PATCH,DELETE)

### Current revision
/matters/:slug/items/:slug/reviewers/ (GET,POST)
    Allow the [lawyer,customer] user to list, and create people who should review
    the attachment
/matters/:slug/items/:slug/reviewers/:reviewer (GET,DELETE)
    Allow the [lawyer,customer] user to list, and delete reviewer
/matters/:slug/items/:slug/reviewers/remind/ (POST)
    Send reminder emails to any outstanding reviewers to please sign

### Historic revision
/matters/:slug/items/:slug/revision/:number/reviewers/ (GET,POST)
/matters/:slug/items/:slug/revision/:number/reviewers/:reviewer (GET,DELETE)
/matters/:slug/items/:slug/revision/:number/reviewers/remind/ (POST)


### Current signatures
/matters/:slug/items/:slug/signatories/ (GET,POST) - these are created within the system and as part of the system flows
    Allow the [lawyer,customer] user to list signatories related to an item
/matters/:slug/items/:slug/signatories/:signatory (GET,DELETE)
    Allow the [lawyer,customer] user to list, and delete signatory
/matters/:slug/items/:slug/signatories/remind/ (POST)
    Send reminder emails to any outstanding signatories to please sign

### Historic signatures
/matters/:slug/items/:slug/revision/:number/signatories/ (GET,POST)
/matters/:slug/items/:slug/revision/:number/signatories/:reviewer (GET,DELETE)
/matters/:slug/items/:slug/revision/:number/signatories/remind/ (POST)


Item details
============

Once we know an items pk/slug/url we can request specific info about them


/items/:slug/comments/ (GET,POST)
    Allow [lawyer,customer] user to list and create comments on an item object

/items/:slug/comments/:comment (GET,PATCH,DELETE)
    Allow [lawyer,customer] user to list, update and delete comments


/items/:slug/activity/ (GET) 
    Allow [lawyer,customer] user to list activity relating to an item object
    Note: These are created within the system and as part
    of the backend.


Revisions
===========

/revisions/ (GET)
    Allow user to list their attachment objects

/revisions/:pk/ (GET,PATCH,DELETE)
    Allow user to view and update the most recent revision (defaults to highest
    revision)

/revisions/:pk/comments/ (GET,POST)
    Allow [lawyer,customer,reviewer,signatory] user to list and create comments on an attachment
    object

/revisions/:pk/activity/ (GET)
    Allow [lawyer,customer,reviewer,signatory] user to list activity on an attachment
