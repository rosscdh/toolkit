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

/matters/:slug/activity/ (GET) - these are created within the system and as part of the system flows
    Allow the [lawyer,customer] user to list activity related to a matter


Matter Items
============

/items/ (GET)
    Allow the [lawyer,customer] user to list items that belong to them

/items/:slug/ (GET,PATCH,DELETE)
    Allow the [lawyer,customer] user to list, and update an existing item
    objects; that belong to them

/items/:slug/attachments/ (GET,POST)
    Allow [lawyer,customer] user to list and create attachment objects for item objects

/items/:slug/workflows/ (GET,POST)
    Allow [lawyer] user to list and associate workflows with an item object

/items/:slug/comments/ (GET,POST)
    Allow [lawyer,customer] user to list and create comments on an item object

/items/:slug/activity/ (GET) - these are created within the system and as part
                               of the system flows
    Allow [lawyer,customer] user to list activity relating to an item object


Attachments
===========

/attachments/ (GET)
    Allow user to list their attachment objects

/attachments/:slug/ (GET,PATCH,DELETE)
    Allow user to view and update the most recent revision (defaults to highest
    revision)
    -- Note A: All Items marked between "Begin: Note A" and "End: Note A" are
       applicable here

/attachments/:slug/revisions/ (GET,POST)
    Allow user to list and create new document revisions

__ Begin: Note A __

/attachments/:slug/revisions/:revision/ (GET,PATCH)
    Allow [lawyer,customer] user to list and update document revisions that
    belong to them

/attachments/:slug/revisions/:revision/comments/ (GET,POST)
    - @DISCUSS do we need this? or are comments at item level acceptable
    Allow [lawyer,customer] user to list and create comments on an attachment
    object

/attachments/:slug/revisions/:revision/activity/ (GET)
    - @DISCUSS do we need this? or is activity at item level acceptable
    Allow [lawyer,customer] user to list activity on an attachment

__ End: Note A __


Workfows
========

/workflows/ (GET)
    Allow [lawyer,customer] user to list public workflow objects

/workflows/:slug/ (GET)
    Allow [lawyer,customer] user to view the details of a specific workflow object
