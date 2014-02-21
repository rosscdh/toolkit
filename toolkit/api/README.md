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


/matters/:matter_slug/ (GET,PATCH,DELETE)
    Allow the [lawyer] user to list, and update an existing matter ("workspace") object


/matters/:matter_slug/items/ (GET,POST)
    Allow the [lawyer,customer] user to list, and create matter items


/matters/:matter_slug/activity/ (GET,POST) - these are created within the system and as part of the system flows
    Allow the [lawyer,customer] user to list activity related to a matter
    POST allows the angular service to send events that are then processed as activity stream items
    @TODO define the params


Matter Items
============

/matters/:matter_slug/items/ (GET)
    Allow the [lawyer,customer] user to list items that belong to them

/matters/:matter_slug/items/:item_slug/ (GET,PATCH,DELETE)
    Allow the [lawyer,customer] user to list, and update an existing item
    objects; that belong to them

# Revisions

reviewers and signatories are represented on the item object, they are actually
derived from the current revision object which is represented on the item.

We can also call specific revisions and access the reviewers and signatories for
that particular revisions.

/matters/:matter_slug/items/:item_slug/revision (GET,POST,PATCH,DELETE)
    [lawyer,customer] to get,create,update,delete the latst revision


### Reviewers

<!-- /matters/:matter_slug/items/:item_slug/revision/reviewers (GET,POST
    [lawyer,customer] to list and create reviewers 
    Method not required as we get the reviewers from the GET :item_slug/revision
    JSON payload
-->
/matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,POST,DELETE)
    [lawyer,customer] to view, create and delete reviewers
/matters/:matter_slug/items/:item_slug/revision/reviewers/remind (GET)
    Send reminder emails to any outstanding reviewers

** Historic revision reviewers **
/matters/:matter_slug/items/:item_slug/revisions/:number/ (GET,POST)


### Signatories

/matters/:matter_slug/items/:item_slug/revision/signatory/:username (GET,POST,DELETE)
    [lawyer,customer] to list,create and delete signatories

/matters/:matter_slug/items/:item_slug/revision/signatories/remind (GET)
    [lawyer,customer] Send reminder emails to any outstanding signatories

** Historic revision signatures **
/matters/:matter_slug/items/:item_slug/revisions/:number/ (GET)



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
