from operator import attrgetter

class LobcderEntry:
    def __init__(self, name, type, size, path):
        self.name = name
        self.type = type
        self.size = size
        self.path = path

def lobcderEntries(files, root, currentPath):
    result = []
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
            result.append(LobcderEntry(name, type, file.size, path))
            result.sort(key = attrgetter('type', 'name'))
    return result