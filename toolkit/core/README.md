Core application
----------------

The core application is made up of a number of modules and services that define
our core architecture.

1. __attachments__ - provides document revisions and related services
2. __client__ - provides access to models for the VERY basic client app, clients are only added via matter.create, we have no interface to them other than that.
3. __item__ - matter.items and related service
4. __mixins__ - generic mixins that are used throughout the app
5. __services__ - various critical services that are used throughout (pusher, mixpanel etc.)
6. __signals__ - currently the activity listener signals are handled here



CONTENT
------------------
1. Permissions API
2. Matter Permissions and implications 



1. Permissions API
------------------


### get our user & matter
```
u = User.objects.get(username='rosslawyer')
m = Workspace.objects.get(slug='ross-and-alexs-test-matter')
```

### get the permissions object for that matter
```
p = u.matter_permissions(matter=m)
```

### see whats part of the permissions object
```
p.PERMISSIONS
p.MATTER_OWNER_PERMISSIONS
p.PRIVILEGED_USER_PERMISSIONS
p.UNPRIVILEGED_USER_PERMISSIONS
p.ANONYMOUS_USER_PERMISSIONS
```

### view users permissions
```
current_permissions = p.permissions 
print current_permissions
```

### set to all permissions
```
all_permissions = dict.fromkeys(p.PERMISSIONS, True)  # set them all to false

p.permissions = all_permissions
print p.permissions
```

### set to no permissions
```
no_permissions = dict.fromkeys(p.PERMISSIONS, False)  # set them all to false

p.permissions = no_permissions
print p.permissions
```

### Update a specific permission for the set
_please note:_ will not add permissions that dont exist in the main p.PERMISSIONS list
```
p.update_permissions(manage_signature_requests=True, manage_clients=False, made_up_permission_that_does_not_exist=True)
print p.permissions  # note that "made_up_permission_that_does_not_exist" is not present
```

### Reset permissions
_resets to the default for whatever their role is_
```
p.reset_permissions()
print p.permissions
```

### Roles
_see the users role for that matter_
```
print p.role
print p.display_role
```

### Dont forget to save the permissions after setting them
```
p.save(update_fields=['data'])
```



2. Matter Permissions and implications
------------------

### workspace.manage_document_reviews
Can manage document reviews:
- invite participant to upload a document
- delete invitation to upload a document which is not mine
- remind user to upload a document

### workspace.manage_items
Can manage checklist items and categories:
- crud categories
- crud items
- delete revisions

### workspace.manage_signature_requests
Can manage signatures & send documents for signature:
- create and delete signing requests

### workspace.manage_clients
Can manage clients:
- crud participants of type 'client'

### workspace.manage_participants
Can manage clients:
- crud participants of any type
-- includes workspace.manage_clients
