Matters
=======


Matters are actually Workspaces; or at least make use of the table and some functionality there


ReactJs
-------

We use reactjs for the matter search functionality

1. edit the matter_search.jsx
2. DO NOT use the matter_search.js for development; this file gets overwritten on deploy; just dont do it


Technical notes
---------------

1. the participants join adds a large amount of overhead to the matter_list view. It is necessary to serialize each participant as they are added to the matter. With a view to lightening this load (upwards of 200 queries if you have many matters)