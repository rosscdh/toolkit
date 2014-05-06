# -*- coding: utf-8 -*-
from toolkit.celery import app


@app.task
def _export_matter(matter):
    for item in matter.item_set.all():  # all items must be completed, otherwise the button wasn't shown
        latest_revision = item.latest_revision

        # download latest_revision
        downloaded_file = latest_revision.ensure_file() if latest_revision else None

        import pdb;pdb.set_trace()

        # create token by: token = signing.dumps(expiry_date, salt=settings.SECRET_KEY)
        # load zip by: signing.loads(get_url_vale, salt=settings.SECRET_KEY)

    # zip collection
    # upload to AWS
    # create token-link to AWS and save
    # send token-link via email