from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import urllib2


def download_file(filedict, revision):
    try:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(filedict.get('url')).read())
        img_temp.flush()
    except:
        raise Exception('Filedownload from URL failed.')

    revision.executed_file.save(filedict.get('filename'), File(img_temp))
    return revision