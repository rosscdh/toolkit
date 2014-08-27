# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand, CommandError

from toolkit.apps.workspace.models import Workspace

from optparse import make_option
from os.path import basename

import dropbox
import logging
logger = logging.getLogger('django.request')


def _safe_matter_name(matter):
    """
    As we dont want the matter.slug to be used (because it has uniquification
    appended to it), we should simply re slugify the matter name
    """
    return slugify(matter.name)


class Command(BaseCommand):
    args = '<matter slug ...>'
    help = "Sync matter with Dropbox.com"

    provider = 'dropbox-oauth2'
    client = None

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

    def valid_token(self, dropbox_provider):
        token = dropbox_provider.tokens
        return token

    def client(self, token):
        client = dropbox.client.DropboxClient(token)
        user = client.account_info()
        return (client, user)

    def participants(self, matter):
        if self.options.get('usernames', None) is not None:
            return matter.participants.filter(username__in=self.options.get('usernames').split())
        # all participants
        return matter.participants.all()

    def full_path(self, path_list):
        return '/%s' % '/'.join(path_list)

    def handle(self, *args, **options):
        self.slugs = args
        self.options = options

        try:
            args[0]
        except IndexError:
            raise CommandError('You must specify at least 1 matter slug')

        for m in self.matters:

            matter_name = _safe_matter_name(m)
            logger.info('Sync to Box: %s' % m.name)

            for p in self.participants(matter=m):

                logger.info('Participant: %s' % p)

                dropbox_provider = p.social_auth.filter(provider=self.provider).first()

                if dropbox_provider:
                    # current_folders = self.current_folders(dropbox_provider=dropbox_provider)
                    token = self.valid_token(dropbox_provider=dropbox_provider)
                    client, user = self.client(token=token)

                    logger.info('TOKEN: %s' % token)

                    # f = Folders(token=token)

                    # if matter_name not in current_folders.keys():
                    #     # does not exist, so create
                    folder_path = []
                    folder_path.append(matter_name)

                    try:
                        client.file_create_folder(path=self.full_path(path_list=folder_path))
                    except Exception as e:
                        logger.info('Folder: /%s Exists' % matter_name)

                    # # create revision files, according to user class
                    for item in m.item_set.all():
                        # reset the path
                        folder_path = []
                        folder_path.append(matter_name)

                        category = slugify(item.category)
                        # Ensure Category
                        if item.category is not None:
                            try:
                                client.file_create_folder(path=self.full_path(path_list=folder_path))
                            except Exception as e:
                                logger.info('Folder: %s Exists' % self.full_path(path_list=folder_path))
                            folder_path.append(category)

                        # Create item folder
                        item_name = slugify(item.name)

                        folder_path.append(item_name)
                        try:
                            client.file_create_folder(path=self.full_path(path_list=folder_path))
                        except Exception as e:
                            logger.info('Folder: %s Exists' % self.full_path(path_list=folder_path))

                        if item.latest_revision:
                            for rev in [item.latest_revision]:
                                rev.ensure_file()
                                target_file = rev.executed_file
                                base_file_name = basename(target_file.name)

                                full_path = self.full_path(path_list=folder_path)

                                logger.debug('Path to file: %s' % full_path)

                                client.put_file(full_path=full_path + '/' + base_file_name, file_obj=target_file, overwrite=True)

                    #     # attachments
                        attachments_list = item.attachments.all()
                        # only create teh folder if we have attachments
                        if attachments_list:
                            full_path = self.full_path(path_list=folder_path) + '/attachments'
                            try:
                                client.file_create_folder(path=full_path)
                            except Exception as e:
                                logger.info('Folder: %s Exists' % full_path)
                            # update the files
                            for attachment in attachments_list:
                                target_file = attachment.attachment
                                base_file_name = basename(target_file.name)
                                client.put_file(full_path=full_path + '/' + base_file_name, file_obj=target_file, overwrite=True)
