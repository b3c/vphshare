from operator import attrgetter
from masterinterface import settings
import requests
import xml.etree.cElementTree as xml

class LobcderEntry:
    def __init__(self, name, type, size, path):
        self.name = name
        self.type = type
        self.size = size
        self.path = path

def getMetadata(path, ticket):
    response = requests.get(settings.LOBCDER_REST + '/items/query?path=' + path, auth = ('user', ticket))
    return response.text

def fillInMetadata(entry, metadata):
    doc = xml.fromstring(metadata)
    found = [element for element in doc.getiterator() if element.text == entry.name]

def lobcderEntries(files, root, currentPath, ticket):
    result = []
    metadata = getMetadata(currentPath, ticket)
    for file in files:
        #removing the LOBCDER root path
        path = file.name.replace(root, '', 1)
        #we do not want to list the root folder
        if path != '/' and path != currentPath:
            type = 'directory' if path.endswith('/') else 'file'
            #ensuring that the path has a slash at the beginning
            if not path.startswith('/'):
                path = '/' + path
            #producing a name from the last component of the path
            name = path if not path.endswith('/') else path.rstrip('/')
            name = name.split('/')[-1]
            entry = LobcderEntry(name, type, file.size, path)
            fillInMetadata(entry, metadata)
            result.append(entry)
            result.sort(key = attrgetter('type', 'name'))
    return result