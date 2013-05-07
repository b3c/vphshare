from operator import attrgetter
from masterinterface import settings
import requests
from lxml import etree as xml
from datetime import datetime
import logging

log = logging.getLogger('cyfronet')

class LobcderPermissions:
    def __init__(self, owner, read, write):
        self.owner = owner
        self.read = read
        self.write = write

class LobcderEntry:
    def __init__(self, name, type, size, path):
        self.name = name
        self.type = type
        self.size = size
        self.path = path
        self.owner = ''
        self.created = None
        self.modified = None
        self.driSupervised = False
        self.driChecksum = None
        self.driValidationDate = None
        self.perms = None
        self.uid = None
        

def getMetadata(path, ticket):
    response = requests.get(settings.LOBCDER_REST + '/items/query?path=' + path, auth = ('user', ticket))
    return response.content

def fillInMetadata(entry, metadata):
    doc = xml.XML(metadata)
    #find logicalDataWrapped element whoose path element contains entry.path
    found = doc.xpath('//path[text()="' + entry.path.rstrip('/') + '"]/..|//path[text()="/' + entry.path.rstrip('/').lstrip('/').replace('/', '//') + '"]/..')[0]
    entry.owner = found.xpath('logicalData/owner')[0].text
    entry.created = datetime.fromtimestamp(float(found.xpath('logicalData/createDate')[0].text)/1000)
    entry.modified = datetime.fromtimestamp(float(found.xpath('logicalData/modifiedDate')[0].text)/1000)
    entry.driSupervised = found.xpath('logicalData/supervised')[0].text.lower() == 'true'
    entry.driChecksum = found.xpath('logicalData/checksum')[0].text
    entry.driValidationDate = datetime.fromtimestamp(float(found.xpath('logicalData/lastValidationDate')[0].text)/1000)
    entry.perms = LobcderPermissions(found.xpath('permissions/owner')[0].text, found.xpath('permissions/read/text()'), found.xpath('permissions/write/text()'))
    entry.uid = found.xpath('logicalData/uid')[0].text

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

def updateMetadata(uid, owner, read, write, driSupervised, ticket):
    perms = xml.Element('permissions')
    ownerElement = xml.Element('owner')
    ownerElement.text = owner
    perms.append(ownerElement)
    if read:
        for r in read.split(','):
            rElement = xml.Element('read')
            rElement.text = r.strip()
            perms.append(rElement)
    if write:
        for w in write.split(','):
            wElement = xml.Element('write')
            wElement.text = w.strip()
            perms.append(wElement)
    requestBody = xml.tostring(perms, pretty_print = True)
    headers = {'content-type': 'application/xml'}
    response = requests.put(settings.LOBCDER_REST + '/item/permissions/' + uid, headers = headers, data = requestBody, auth = ('user', ticket))
    log.debug('LOBCDER permission update response url, code and content: ' + response.url + ', ' + str(response.status_code) + ' - ' + response.content)
    response = requests.put(settings.LOBCDER_REST + '/item/dri/' + uid + '/supervised/' + 'TRUE' if driSupervised else 'FALSE', auth = ('user', ticket))
    log.debug('LOBCDER DRI supervised update response url, code and content: ' + response.url + ', ' + str(response.status_code) + ' - ' + response.content)