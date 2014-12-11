import requests
import shutil
from numbers import Number
from httplib import responses as HTTP_CODES
from urlparse import urlparse
import xml.etree.cElementTree as xml
from collections import namedtuple
from cStringIO import StringIO
import urllib

class WebdavException(Exception):
    pass

class ConnectionFailed(WebdavException):
    pass


def codestr(code):
    return HTTP_CODES.get(code, 'UNKNOWN')


File = namedtuple('File', ['name', 'size', 'mtime', 'ctime'])


def prop(elem, name, default=None):
    child = elem.find('.//{DAV:}' + name)
    return default if child is None or child.text is None else child.text


def elem2file(elem):
    return File(
        urllib.unquote(prop(elem, 'href')),
        int(prop(elem, 'getcontentlength', 0)),
        prop(elem, 'getlastmodified', ''),
        prop(elem, 'creationdate', ''),
    )


class OperationFailed(WebdavException):
    _OPERATIONS = dict(
        GET = "download",
        PUT = "upload",
        DELETE = "delete",
        MKCOL = "create directory",
        PROPFIND = "list directory",
        COPY = "copy resource",
        )
    def __init__(self, method, path, expected_code, actual_code):
        self.method = method
        self.path = path
        self.expected_code = expected_code
        self.actual_code = actual_code
        operation_name = self._OPERATIONS[method]
        self.reason = 'Failed to {operation_name} "{path}"'.format(**locals())
        expected_codes = (expected_code,) if isinstance(expected_code, Number) else expected_code
        expected_codes_str = ", ".join('{0} {1}'.format(code, codestr(code)) for code in expected_codes)
        actual_code_str = codestr(actual_code)
        msg = '''\
{self.reason}.
  Operation     :  {method} {path}
  Expected code :  {expected_codes_str}
  Actual code   :  {actual_code} {actual_code_str}'''.format(**locals())
        super(OperationFailed, self).__init__(msg)

class Client(object):
    def __init__(self, host, port=0, auth=None, username=None, password=None,
                 protocol='http'):
        if not port:
            port = 443 if protocol == 'https' else 80
        self.baseurl = '{0}://{1}:{2}'.format(protocol, host ,port)
        self.cwd = '/'
        self.session = requests.session()
        if auth:
            self.session.auth = auth
        elif username and password:
            self.session.auth = (username, password)
    def _send(self, method, path, expected_code, **kwargs):
        url = self._get_url(path)
        response = self.session.request(method, url, allow_redirects=False, verify=False, **kwargs)
        if isinstance(expected_code, Number) and response.status_code != expected_code \
            or not isinstance(expected_code, Number) and response.status_code not in expected_code:
            raise OperationFailed(method, path, expected_code, response.status_code)
        return response
    def _get_url(self, path):
        path = str(path).strip()
        if path.startswith('/'):
            return self.baseurl + path
        return "".join((self.baseurl, self.cwd, path))
    def cd(self, path):
        path = path.strip()
        if not path:
            return
        stripped_path = '/'.join(part for part in path.split('/') if part) + '/'
        if stripped_path == '/':
            self.cwd = stripped_path
        elif path.startswith('/'):
            self.cwd = '/' + stripped_path
        else:
            self.cwd += stripped_path
    def mkdir(self, path, safe=False):
        expected_codes = 201 if not safe else (201, 301)
        self._send('MKCOL', path, expected_codes)
    def mkdirs(self, path):
        dirs = [d for d in path.split('/') if d]
        if not dirs:
            return
        if path.startswith('/'):
            dirs[0] = '/' + dirs[0]
        old_cwd = self.cwd
        try:
            prev_dir = dirs[0] + "/" + dirs[1] + "/" # this should be equivalent to LOBCDER_ROOT_IN_WEBDAV
            for i in range(2, len(dirs)):
                prev_dir = prev_dir + dirs[i] + "/"
                if not self.exists(prev_dir):
                    self.mkdir(prev_dir, safe=True)
        finally:
            self.cd(old_cwd)
    def rmdir(self, path, safe=False):
        path = str(path).rstrip('/') + '/'
        expected_codes = 204 if not safe else (204, 404)
        self._send('DELETE', path, expected_codes)
    def delete(self, path):
        self._send('DELETE', path, 204)
    def upload(self, local_path, remote_path):
        with open(local_path, 'rb') as f:
            self._send('PUT', remote_path, (201, 204), data=f.read())
    def uploadChunks(self, chunks, remote_path):
        self._send('PUT', remote_path, (201, 204), data = chunks)
    def download(self, remote_path, local_path):
        response = self._send('GET', remote_path, 200, stream = True)
        with open(local_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
    def downloadChunks(self, remote_path):
        response = self._send('GET', remote_path, 200, stream = True)
        return response
    def ls(self, remote_path='.'):
        headers = {'Depth': '1'}
        response = self._send('PROPFIND', remote_path, (207, 301), headers=headers)

        # Redirect
        if response.status_code == 301:
            url = urlparse(response.headers['location'])
            return self.ls(url.path)

        tree = xml.parse(StringIO(response.content))
        #print response.content
        return [elem2file(elem) for elem in tree.findall('{DAV:}response')]
    def exists(self, path):
        headers = {'Depth': '0'}
        try:
            response = self._send('PROPFIND', path, (207, 301), headers = headers)
        except OperationFailed as e:
            if e.actual_code == 404:
                return False
            else:
                raise e
        return True
    def copy(self, fromPath, toPath, overwrite = False):
        expectedCodes = (201, 204)
        fromUrl = self._get_url(fromPath)
        toUrl = self._get_url(toPath)
        response = self.session.request('COPY', fromUrl, verify=False, headers = {'Destination': toUrl, 'Overwrite': 'T' if overwrite else 'F'})
        if response.status_code not in expectedCodes:
            raise OperationFailed('COPY', fromUrl + ' -> ' + toUrl, expectedCodes, response.status_code)
    def getType(self, path):
        headers = {'Depth': '0'}
        try:
            response = self._send('PROPFIND', path, (207, 301), headers = headers)
            tree = xml.parse(StringIO(response.content))
            elements = [elem2file(elem) for elem in tree.findall('{DAV:}response')]
            if len(elements) == 1:
                if elements[0].name.endswith('/'):
                    return 'folder'
                else:
                    return 'file'
            else:
                raise OperationFailed('PROPFIND', 'There should be only one element for ' + path, expectedCodes, response.status_code)
        except OperationFailed as e:
            if e.actual_code == 404:
                return None
            else:
                raise e