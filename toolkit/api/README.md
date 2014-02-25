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

__ prefix: /api/v1/ __

Account
=======

As an authenticated user
I need to be able to update my account info
so that I can change my password and email and various details

/account/ (GET,PATCH)
    Allow the [lawyer,customer] user to modify various aspects of their account; automatically
    patches only their account based on session.

PATCH
```

```

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

POST new matter
```
{
    "name": "LawPal (internal)", 
    "client": null, 
    "lawyer": "http://localhost:8000/api/v1/users/rosslawyer/", 
    "participants": [
        "http://localhost:8000/api/v1/users/rossc/"
    ]
}
```

/matters/:matter_slug/ (GET,PATCH,DELETE)
    Allow the [lawyer] user to list, and update an existing matter ("workspace") object

### Categories
/matters/:matter_slug/category/:category (GET,POST,DELETE)
    [lawyer] can assign an item to a category


### Closing Groups
/matters/:matter_slug/closing_group/:group (GET,POST,DELETE)
    [lawyer] can assign an item to a closing group


Matter Items
============

/matters/:matter_slug/items/ (GET,POST)
    Allow the [lawyer,customer] user to list items that belong to them

POST
```
{
    "status": "New",
    "name": "test again",
    "description": "stuff goes here",
    "matter": "http://localhost:8000/api/v1/matters/lawpal-internal/",
    "parent": null,
    "children": [],
    "closing_group": null,
    "latest_revision": null,
    "is_final": false,
    "is_complete": false,
    "date_due": null
}
```

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

POST
```
{
    "executed_file": "", 
    "item": "http://localhost:8000/api/v1/matters/lawpal-internal/items/4bcfaef627864c61a2a731473d40470e/",
    "uploaded_by": "http://localhost:8000/api/v1/users/rosslawyer/"
    "reviewers": null, 
    "signatories": null, 
    "revisions": []
}
```


### Reviewers

/matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,POST,DELETE)
    [lawyer,customer] to view, create and delete reviewers
/matters/:matter_slug/items/:item_slug/revision/reviewers/remind (POST)
    Send reminder emails to any outstanding reviewers

** Historic revision reviewers **
/matters/:matter_slug/items/:item_slug/revisions/:number/ (GET,POST)


### Signatories

/matters/:matter_slug/items/:item_slug/revision/signatory/:username (GET,POST,DELETE)
    [lawyer,customer] to list,create and delete signatories

/matters/:matter_slug/items/:item_slug/revision/signatories/remind (POST)
    [lawyer,customer] Send reminder emails to any outstanding signatories

** Historic revision signatures **
/matters/:matter_slug/items/:item_slug/revisions/:number/ (GET)


Item details
============

Once we know an items id we can request specific info about them

### Comments
/matters/:matter_slug/items/:item_slug/comments/ (GET,POST)
    Allow [lawyer,customer] user to list and create comments on an item object

/matters/:matter_slug/items/:item_slug/comments/:comment (GET,PATCH,DELETE)
    Allow [lawyer,customer] user to list, update and delete comments

### Activity
/matters/:matter_slug/items/:item_slug/activity/ (GET) 
    Allow [lawyer,customer] user to list activity relating to an item object
    Note: These are created within the system and as part
    of the backend.
