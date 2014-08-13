# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from toolkit.apps.workspace.models import Workspace

from optparse import make_option
from social.apps.django_app.sa_default.models import UserSocialAuth
from box.box import Me, Folders, Files, UploadFiles

import hashlib


def _safe_matter_name(matter):
    """
    As we dont want the matter.slug to be used (because it has uniquification
    appended to it), we should simply re slugify the matter name
    """
    return slugify(matter.name)


def _file_sha1(target_file):
    """
    Box requires Content-MD5 to be set has a sha1 of the file contents
    """
    sha = hashlib.sha1()
    
    with default_storage.open(target_file) as f:
        while True:
            block = f.read(2**10) # Magic number: one-megabyte blocks.
            if not block: break
            sha.update(block)
        return sha.hexdigest()


class Command(BaseCommand):
    args = '<matter slug ...>'
    help = "Sync matter with Box.com"

    provider = 'box'

    slugs = []

    option_list = BaseCommand.option_list + (
        make_option('-u', '--usernames',
            action='store',
            dest='usernames',
            default=None,
            type='string',
            help='usernames seperated by a ,'),
        )

    @property
    def matters(self):
        return Workspace.objects.filter(slug__in=self.slugs)

    def current_folders(self, box_provider):
        return dict((f.get('name'), f.get('id')) for f in self.folders(box_provider=box_provider))

    def matter_folder_id(self, name, current_folders):
        try:
            return [id for folder_name, id in current_folders.iteritems() if folder_name == name][0]
        except IndexError:
            raise Exception('could not find folder: %s in current folders: %s' % (name, current_folders))

    def valid_token(self, box_provider):
        token = box_provider.tokens

        me = Me(token=token)
        me.options()

        if me.response.ok is False:
            print('%s: %s' % (me.response.status_code, me.response.reason))
            self.refresh_token(social_auth_provider=box_provider)
            token = box_provider.tokens

        return token


    def refresh_token(self, social_auth_provider):
        refresh_token = social_auth_provider.extra_data.get('refresh_token') 
        updated_data = social_auth_provider.get_backend_instance().refresh_token(token=refresh_token)
        # update the providers token
        social_auth_provider.extra_data.update(updated_data)
        social_auth_provider.save(update_fields=['extra_data'])
        return social_auth_provider

    def folders(self, box_provider, parent={'id': 0}):
        token = box_provider.tokens

        f = Folders(token=token)
        folders = f.get(id=0, parent=parent)

        return [f for f in folders.get('item_collection', {}).get('entries', []) if f.get('type') == 'folder']

    def participants(self, matter):
        if self.options.get('usernames', None) is not None:
            return matter.participants.filter(username__in=self.options.get('usernames').split())
        # all participants
        return matter.participants.all()

    def handle(self, *args, **options):
        self.slugs = args
        self.options = options

        try:
            args[0]
        except IndexError:
            raise CommandError('You must specify at least 1 matter slug')

        for m in self.matters:

            matter_name = _safe_matter_name(m)

            for p in self.participants(matter=m):

                print('Participant: %s' % p)

                box_provider = p.social_auth.filter(provider=self.provider).first()

                if box_provider:

                    current_folders = self.current_folders(box_provider=box_provider)
                    token = self.valid_token(box_provider=box_provider)
                    print('TOKEN: %s' % token)

                    f = Folders(token=token)

                    if matter_name not in current_folders.keys():
                        # does not exist, so create
                        resp = f.post(name=matter_name, parent={'id': 0})
                        current_folders = self.current_folders(box_provider=box_provider)

                    matter_folder_id = self.matter_folder_id(name=matter_name, current_folders=current_folders)

                    # create revision files, according to user class
                    for item in m.item_set.all():
                        parent_id = matter_folder_id

                        # Ensure Category
                        if item.category is not None:

                            resp = f.post(name=slugify(item.category), parent={'id': matter_folder_id})

                            try:
                                parent_id = resp.get('id') if resp.get('id', None) is not None else f.response.json().get('context_info', {}).get('conflicts',[])[0].get('id', None)
                            except IndexError:
                               parent_id = matter_folder_id

                        print('matter: %s parent: %s' % (matter_folder_id, parent_id))

                        #for rev in item.revision_set.all():
                        if item.latest_revision:
                            for rev in [item.latest_revision]:
                                rev.ensure_file()
                                target_file = rev.executed_file
                                fl = UploadFiles(token=token, sha1=_file_sha1(target_file=target_file))
                                print('uploading with parent: %s' % (parent_id,))
                                resp = fl.post(files={'file': default_storage.open(target_file)}, parent_id=parent_id)
                                print fl.response.content
