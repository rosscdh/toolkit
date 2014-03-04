Project Components
------------------


Matters
=======

create edit delete
open closed


Clients
=======

Clients are a simple bag of metadata that allow us to associate matters with them
no explicit relationship is made with users and clients (yet) but this may be done
after mvp


Members
=======

create delete
on delete: deleted members cant access matter/items other related; notifications are no longer sent to them


Search
=======

2 types 1 interface

"filter" on keyup does basic javascript matching on title and description for items as well as closing_group
if the user hits enter a search panel shows and the results of a deep-search are shown (elastic search)


Items
-----

1. Items provide access to a documents revisions as well as an interface to allow commenting and feedback
2. Can belong to a category but this is not mandatory
3. Soft Delted
4. they always provide access to the latest_revision by default
5. they provide acess to all revision


Super Powers (1 ups)
--------------------

Are routines 




Item Reviewers
==============

1. Are invited explicitly
2. have access only to the revision they are explicitly associated with


Item Signatories
================

1. Are invited explicitly
2. have access only to the revision they are explicitly associated with


Permissions
===========

Permissions are on a simple level basis

matter level : has access to the matter, al lof the matters items, and all of the items revisions
item level : has access ony to the item and its revisions
revision level : has access only to the revision and can read some of the item info but can only comment on.


Security
========

1. use https://github.com/authy/authy-python to implement 2 step auth for added Lawyer and Client only security
2. implies that when the lawyer/cietn logs in from another device they will be authenticated via sms
3. review + signature urls expire after 14 days


Matter Templates
----------------

1. in dev set a matter up as you want it
2. manage.py dumpdata matter item > name_of_template.json
3. need an interface to load a template as a new matter (drop down list select and create)


Tasks
-----

1. 2 step auth for clients and lawyers when using Authy python-authy
2. Google Doc Edit and save update locally
3. search integration using Haystack + Elastic search + Realtime Model
4. Backup all documents + revisions to dropbox structure /lawpal/:matter-name/final && /lawpal/:matter-name/drafts && /lawpal/:matter-name/executed
5. subscription plan
6. docusign alternative to hello-sign
7. Blog



TODO

1. matter needs description field
1a. matter status/archived concept
2. angular helper to degrade avatar to initials
3. 