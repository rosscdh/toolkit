from sets import Set

cloned_matters = Set()
found_revisions = Set()
revision_matters = {}

for i in Item.objects.all().values():
    latest_revision_id = i.get('latest_revision_id', None)
    if latest_revision_id:
        if latest_revision_id in found_revisions:
            cloned_matters.add(i.get('matter_id'))
        else:
            found_revisions.add(latest_revision_id)
        # set up the set and ad the matter to it
        matter_id = str(i.get('matter_id'))
        tmp_matter_items = getattr(revision_matters, matter_id, Set())
        tmp_matter_items.add(latest_revision_id)
        revision_matters[matter_id] = tmp_matter_items

print "Found %d potential cloned matters: %s" % (len(cloned_matters), Workspace.objects.filter(pk__in=cloned_matters))

for m in Workspace.objects.filter(pk__in=cloned_matters):
    print "Matter: %s owned by %s is potentially cloned because it has items that have a shared latest_revision: %s" % (m, m.lawyer, revision_matters[str(m.pk)])
    for matter, rev in revision_matters.iteritems():
        if revision_matters[str(m.pk)].intersection(rev):
            print '%s %s' % (matter, rev)

    print [i.matter for i in Item.objects.filter(latest_revision__in=revision_matters[str(m.pk)])]



for m in Workspace.objects.deleted(pk__in=cloned_matters):
    print "Deleted Matter: %s owned by %s is potentially cloned because it has items that have a shared latest_revision: %s" % (m, m.lawyer, revision_matters)


Matter: Demo owned by Yael Citro is potentially cloned because it has items that have a shared latest_revision: Set([91])
[<Workspace: LawPal Corporate SetUp/Seed Financing>, <Workspace: ross test clon>, <Workspace: Demo>]

__reparative action__

[w.item_set.model.objects.filter(matter=w).update(latest_revision=None) for w in Workspace.objects.filter(slug__in=['demo', 'ross test clon'])]

### next ###

Matter: LawPal Corporate SetUp/Seed Financing owned by Yael Citro is potentially cloned because it has items that have a shared latest_revision: Set([149])
[<Workspace: Demo>, <Workspace: LawPal Corporate SetUp/Seed Financing>, <Workspace: ross test clon>]

__reparative action__

[w.item_set.model.objects.filter(matter=w).update(latest_revision=None) for w in Workspace.objects.filter(slug__in=['demo', 'ross test clon'])]


### next ###

Matter: anohter clone safe delete owned by Ross Crawford is potentially cloned because it has items that have a shared latest_revision: Set([242])
[<Workspace: anohter clone safe delete>, <Workspace: Ross and Alex's Test Matter>]

__reparative action__

[w.item_set.model.objects.filter(matter=w).update(latest_revision=None) for w in Workspace.objects.filter(slug__in=['anohter-clone-safe-delete'])]


### next ###

Matter: matter2 owned by armand martin is potentially cloned because it has items that have a shared latest_revision: Set([269])
[<Workspace: matter1>, <Workspace: matter2>]

__reparative action__

[w.item_set.model.objects.filter(matter=w).update(latest_revision=None) for w in Workspace.objects.filter(slug__in=['matter2'])]

[w.item_set.model.objects.filter(matter=w) for w in Workspace.objects.filter(slug__in=['matter2'])]

### next ###

Matter: ross test clon owned by Ross Crawford is potentially cloned because it has items that have a shared latest_revision: Set([149])
[<Workspace: Demo>, <Workspace: LawPal Corporate SetUp/Seed Financing>, <Workspace: ross test clon>]

[w.item_set.model.objects.filter(matter=w).update(latest_revision=None) for w in Workspace.objects.filter(slug__in=['demo', 'ross-test-clon'])]


## Running these repairs ##

