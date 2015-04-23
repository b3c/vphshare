from operator import attrgetter
from masterinterface import settings
import requests
from lxml import etree as xml
from datetime import datetime, timedelta
import logging

log = logging.getLogger('cyfronet')

class LobcderException(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
    def __str__(self):
        return repr(self.message)

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
        self.format = None
        self.created = None
        self.modified = None
        self.driSupervised = False
        self.driChecksum = None
        self.driValidationDate = None
        self.perms = None
        self.uid = None

def getShortTicket(ticket):
    response = requests.get('https://lobcder.vph.cyfronet.pl/lobcder/urest/getshort/' + ticket, verify=False)
    return response.content

def getMetadata(path, ticket):
    response = requests.get(settings.LOBCDER_REST_URL + '/items/query?path=' + path, auth = ('user', ticket))
    return response.content

def fillInMetadata(entry, metadata):
    doc = xml.XML(metadata)
    #find logicalDataWrapped element whose path element contains entry.path
    foundElements = doc.xpath('//path[text()="' + entry.path.rstrip('/') + '"]/..|//path[text()="/' + entry.path.rstrip('/').lstrip('/').replace('/', '//') + '"]/..')
    if len(foundElements) > 0:
        found = foundElements[0]
        entry.owner = found.xpath('logicalData/owner')[0].text
        entry.created = datetime.fromtimestamp(float(found.xpath('logicalData/createDate')[0].text)/1000)
        entry.modified = datetime.fromtimestamp(float(found.xpath('logicalData/modifiedDate')[0].text)/1000)
        entry.driSupervised = found.xpath('logicalData/supervised')[0].text.lower() == 'true'
        entry.driChecksum = _get_first_tag_text(found, 'logicalData/checksum')
        entry.driValidationDate = datetime.fromtimestamp(float(_get_first_tag_text(found, 'logicalData/lastValidationDate'))/1000)
        entry.perms = LobcderPermissions(found.xpath('permissions/owner')[0].text, found.xpath('permissions/read/text()'), found.xpath('permissions/write/text()'))
        entry.uid = found.xpath('logicalData/uid')[0].text
    else:
        log.warn('Could not find LOBCDER metadata for ' + entry.path)

def _get_first_tag_text(doc, xpath_expression):
    elements = doc.xpath(xpath_expression)
    return elements[0].text if len(elements) > 0 else None

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
            if type == 'file' and len(entry.name.split('.')) > 1:
                entry.format = entry.name.split('.')[-1].lower()
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
    response = requests.put(settings.LOBCDER_REST_URL + '/item/permissions/' + uid, headers = headers, data = requestBody, auth = ('user', ticket))
    log.debug('LOBCDER permission update response url, code and content: ' + response.url + ', ' + str(response.status_code) + ' - ' + response.content)
    if response.status_code != 204:
        raise LobcderException('LOBCDER permissions could not be updated and returned code ' + str(response.status_code), str(response.status_code))
    response = requests.put(settings.LOBCDER_REST_URL + '/item/dri/' + uid + '/supervised/' + ('TRUE' if driSupervised else 'FALSE'), auth = ('user', ticket))
    log.debug('LOBCDER DRI supervised update response url, code and content: ' + response.url + ', ' + str(response.status_code) + ' - ' + response.content)
    if response.status_code != 204:
        raise LobcderException('LOBCDER DRI flag could not be updated and returned code ' + str(response.status_code), str(response.status_code))

def extractEntriesFromMetadata(metadata):
    doc = xml.XML(metadata)
    entries = []
    for pathElement in doc.xpath('//path'):
        #omitting root element
        if pathElement.text == '/':
            continue
        name = pathElement.getparent().xpath('logicalData/name/text()')[0]
        type = 'file' if pathElement.getparent().xpath('logicalData/type/text()')[0] == 'logical.file' else 'directory'
        size = pathElement.getparent().xpath('logicalData/length/text()')[0]
        path = pathElement.text + ('/' if type == 'directory' else '')
        if path == '/':
            continue
        entry = LobcderEntry(name, type, size, path)
        fillInMetadata(entry, metadata)
        entries.append(entry)
    entries.sort(key = attrgetter('type', 'path'))
    return entries

def lobcderQuery(resourceName, createdAfter, createdBefore, modifiedAfter, modifiedBefore, ticket):
    params = {}
    createdAfterSeconds = '0'
    createdBeforeSeconds = (datetime.now() + timedelta(days=1)).strftime('%s')
    modifiedAfterSeconds = '0'
    modifiedBeforeSeconds = (datetime.now() + timedelta(days=1)).strftime('%s')
    if createdAfter:
        createdAfterSeconds = datetime.strptime(createdAfter, '%m-%d-%Y').strftime('%s')
    if createdBefore:
        createdBeforeSeconds = datetime.strptime(createdBefore, '%m-%d-%Y').strftime('%s')
    if modifiedAfter:
        modifiedAfterSeconds = datetime.strptime(modifiedAfter, '%m-%d-%Y').strftime('%s')
    if modifiedBefore:
        modifiedBeforeSeconds = datetime.strptime(modifiedBefore, '%m-%d-%Y').strftime('%s')
    params = {'path': '/', 'name': resourceName, 'cStartDate': createdAfterSeconds, 'cEndDate': createdBeforeSeconds, 'mStartDate': modifiedAfterSeconds, 'mEndDate': modifiedBeforeSeconds}
    response = requests.get(settings.LOBCDER_REST_URL + '/items/query', params = params, auth = ('user', ticket))
    metadata = response.content
    return extractEntriesFromMetadata(metadata)
