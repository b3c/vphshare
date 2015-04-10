__author__ = 'pa'
_author_ = 'Alfredo Saglimbeni'
_email_ = 'a.saglimbeni@scsitaly.com'

import os, random, struct, string, sys
from xmlrpclib import ServerProxy
from shutil import *
from Crypto.Cipher import DES3
from Crypto.Hash import HMAC, SHA
import commands
import hashlib
import subprocess
from xmlrpclib import ServerProxy
from lxml import etree
import easywebdav
from config import *


binary_path = "/scs/app/www/Storage"

BOTAN = '/scs/app/www/MAFlib/Build/bin/botanApp'

REPOSITORY_TO_MIGRATE = ['IOR_LTM', 'ancaimi88', 'desmfryan', 'farinella', 'gcasaroli', 'msv', 'rer_universita', 'roncari', 'sintjans', 'tassani', 'testi', 'testuser', 'viceconti', 'vphop-project', 'xzhao', 'jgosai']
GROUPS = ['msv', 'rer_universita', 'vphop-project']
LOCKUP_MIGRATION = {'IOR_LTM':'schileo', 'ancaimi88':'viceconti', 'desmfryan':'plawford', 'farinella':'viceconti', 'gcasaroli': 'viceconti', 'LauraMecozzi':'Baruffaldi', 'testuser':'schileo'}
LOBCDER_HOST = 'lobcder.vph.cyfronet.pl'
LOBCDER_ROOT = '/lobcder/dav'
LOBCDER_PORT = 443
def mode_folder_in_dav(ticket, source, destination):
    webdav = easywebdav.connect(LOBCDER_HOST, LOBCDER_PORT, username='admin', password=ticket, protocol = 'https')
    webdav.upload(source,destination)

class EncryptionMigration (object):

    destFolder = '/scs/app/www/Storage2/'
    PSurl = None
    binaryDir = None
    server = None
    username = None
    password = None
    good_binaries = []
    data_encrypted = []

    def __init__(self, username , password, PSurl , binaryDir ):

        self.PSurl = PSurl
        self.binaryDir = binaryDir
        self.username = username
        self.password = password
        self.server =  ServerProxy("https://%s:%s@%s/" % (username, password,PSurl) )

    def getBinaryUri(self):

        good_binaries = self.server.getAllBinaryURIs()
        all_binaries = os.listdir(self.binaryDir)
        for dataresources in good_binaries:
            for myBin in dataresources:
                if myBin[1] in all_binaries:
                    self.good_binaries.append(myBin)

        return self.good_binaries

    def id_generator(self , size=32, chars=string.ascii_lowercase+ string.ascii_uppercase + string.digits ):
        chars="0123456789ABCDEF"
        return ''.join(random.choice(chars) for x in range(size))

    def getPassphrase(self, dataresourceUrl):

        dataServer= ServerProxy(dataresourceUrl.replace('http://','http://'+self.username+':'+self.password+'@'))
        passphrase = dataServer.getPassphrase()
        return passphrase

    def setPassPhrase(self, dataresourceUrl, passphrase):
        try:
            dataServer= ServerProxy(dataresourceUrl.replace('http://','http://'+self.username+':'+self.password+'@'))
            dataServer.setPassphrase(passphrase)
        except:
            raise 'Error during set passphrase of %s' % (dataresourceUrl)

    def decypt_file(self,passphrase, in_filename, out_filename):

        cmdResult=commands.getstatusoutput('%s D %s %s %s'%(BOTAN, in_filename,out_filename,passphrase))
        return cmdResult

    def decryptOneBinary(self, dataresource):
        binaryCopied= open('/tmp/binaryCopied.csv','w')
        statTotalFile=0
        statTotalData=0
        listCopied = {}
        good_binaries = self.server.getAllBinaryURIs()
        all_binaries = os.listdir(self.binaryDir)
        encrypt_dir = os.listdir(self.destFolder)
        try:
            for dataresourceid in good_binaries:
                dataresources = good_binaries[dataresourceid]
                if dataresourceid == dataresource:
                    for myBin in dataresources:

                        passphrase= self.getPassphrase(myBin[2])
                        remotePass = passphrase
                        if myBin[1] != '' and myBin[1] != 'NOT PRESENT':

                            #check if binary exist into Storage directory
                            if ((myBin[1] in all_binaries) and (myBin[1] not in encrypt_dir)):

                                #check if binary already encrypted
                                if (listCopied.get(myBin[1],None) is None) :

                                    self.decypt_file(passphrase,self.binaryDir+myBin[1],self.destFolder+myBin[1])
                                    listCopied[myBin[1]]=passphrase

                                else:

                                    passphrase = listCopied[myBin[1]]

                                info = os.stat( self.binaryDir+myBin[1])

                                statTotalData += info.st_size

                                statTotalFile+=1

                                add = str(statTotalFile)+': '+ str(myBin[0])+','+str(myBin[1])+','+str(myBin[2])+','+str(passphrase)+','+str(remotePass)+','+str(info.st_size)
                                print add
                                binaryCopied.write(add+'\n')

                            else:
                                if (myBin[1] not in all_binaries):
                                    add = str(statTotalFile)+': '+str(myBin[0])+','+str(myBin[1])+','+str(myBin[2])+','+str(passphrase)+','+str(remotePass)+': WARNING binary is not in Storange directory'
                                    print add
                                    binaryCopied.write(add+'\n')

        except Exception, e:

            print e
            binaryCopied.write(str(e)+'\n')
            binaryCopied.close()
            return

        binaryCopied.close()

    def encryptOneBinary(self, dataresource):
        binaryCopied= open('/tmp/binaryCopied.csv','w')
        statTotalFile=0
        statTotalData=0
        listCopied = {}
        good_binaries = self.server.getAllBinaryURIs()
        all_binaries = os.listdir(self.binaryDir)
        encrypt_dir = os.listdir(self.destFolder)
        try:
            for dataresourceid in good_binaries:
                #generate passpharase
                passphrase = self.id_generator(size=32)
                dataresources = good_binaries[dataresourceid]
                if dataresourceid == dataresource:
                    for myBin in dataresources:

                        remotePass= self.getPassphrase(myBin[2])
                        if remotePass is None:
                            self.setPassPhrase(myBin[2],passphrase)
                            remotePass= self.getPassphrase(myBin[2])
                        else:
                            passphrase=remotePass

                        if myBin[1] != '' and myBin[1] != 'NOT PRESENT':

                            #check if binary exist into Storage directory
                            if ((myBin[1] in all_binaries) and (myBin[1] not in encrypt_dir)):

                                #check if binary already encrypted
                                if (listCopied.get(myBin[1],None) is None) :

                                    self.encrypt_file(passphrase,self.binaryDir+myBin[1],self.destFolder+myBin[1])
                                    listCopied[myBin[1]]=passphrase

                                else:

                                    passphrase = listCopied[myBin[1]]
                                    self.setPassPhrase(myBin[2],passphrase)
                                    remotePass= self.getPassphrase(myBin[2])


                                info = os.stat( self.binaryDir+myBin[1])

                                statTotalData += info.st_size

                                statTotalFile+=1

                                add = str(statTotalFile)+': '+ str(myBin[0])+','+str(myBin[1])+','+str(myBin[2])+','+str(passphrase)+','+str(remotePass)+','+str(info.st_size)
                                print add
                                binaryCopied.write(add+'\n')

                            else:
                                if (myBin[1] not in all_binaries):
                                    add = str(statTotalFile)+': '+str(myBin[0])+','+str(myBin[1])+','+str(myBin[2])+','+str(passphrase)+','+str(remotePass)+': WARNING binary is not in Storange directory'
                                    print add
                                    binaryCopied.write(add+'\n')

        except Exception, e:

            print e
            binaryCopied.write(str(e)+'\n')
            binaryCopied.close()
            return

        binaryCopied.close()

    def encryptBinary(self, targetDataresource=None):
        binaryCopied= open('/tmp/binaryCopied.csv','w')
        statTotalFile=0
        statTotalData=0
        listCopied = {}
        good_binaries = self.server.getAllBinaryURIs()
        all_binaries = os.listdir(self.binaryDir)
        encrypt_dir = os.listdir(self.destFolder)
        try:
            for dataresourceid in good_binaries:
                #generate passpharase
                passphrase = self.id_generator(size=32)
                dataresources = good_binaries[dataresourceid]

                if targetDataresource is not None and dataresourceid != targetDataresource:
                    continue

                for myBin in dataresources:

                    remotePass= self.getPassphrase(myBin[2])
                    if remotePass is None:
                        self.setPassPhrase(myBin[2],passphrase)
                        remotePass= self.getPassphrase(myBin[2])
                    else:
                        passphrase=remotePass

                    if myBin[1] != '' and myBin[1] != 'NOT PRESENT':

                        #check if binary exist into Storage directory
                        if ((myBin[1] in all_binaries) and (myBin[1] not in encrypt_dir)):

                            #check if binary already encrypted
                            if listCopied.get(myBin[1],None) is None:

                                self.encrypt_file(passphrase,self.binaryDir+myBin[1],self.destFolder+myBin[1])
                                listCopied[myBin[1]]=passphrase

                            else:

                                passphrase = listCopied[myBin[1]]
                                self.setPassPhrase(myBin[2],passphrase)
                                remotePass= self.getPassphrase(myBin[2])


                            info = os.stat( self.binaryDir+myBin[1])

                            statTotalData += info.st_size

                            statTotalFile+=1

                            # get old md5 value
                            dataServer = ServerProxy(myBin[2].replace('http://','http://'+self.username+':'+self.password+'@'))
                            oldmd5 = dataServer.xml_read('L0000_resource_data_Dataset_LocalFileCheckSum')

                            # calculate md5 and set md5 valut to physiomespace
                            m = hashlib.md5()
                            myBinFd = open( self.destFolder+myBin[1], "rb" )
                            binaryContent = myBinFd.read()
                            m.update( binaryContent )
                            md5 = m.hexdigest()

                            # get size and set value to physiomespace
                            params = { 'name': ['L0000_resource_data_Dataset_LocalFileCheckSum','L0000_resource_data_Size_FileSize'],
                                       'new' : [str(md5), str(len(binaryContent))] }

                            dataServer.xml_edit( params )

                            add = str(statTotalFile)+': '+ str(myBin[0])+','+str(myBin[1])+','+str(myBin[2])+','+str(passphrase)+','+str(remotePass)+','+str(info.st_size) +','+str(len(binaryContent))+','+str(oldmd5)+','+str(md5)
                            print add
                            binaryCopied.write(add+'\n')


                        else:
                            if (myBin[1] not in all_binaries):
                                add = str(statTotalFile)+': '+str(myBin[0])+','+str(myBin[1])+','+str(myBin[2])+','+str(passphrase)+','+str(remotePass)+': WARNING binary is not in Storage directory'
                                print add
                                binaryCopied.write(add+'\n')

        except Exception, e:

            print e
            binaryCopied.write(str(e)+'\n')
            binaryCopied.close()
            return

        binaryCopied.close()


    def encrypt_file(self,passphrase, in_filename, out_filename):

        cmdResult=commands.getstatusoutput('%s E %s %s %s'%(BOTAN, in_filename,out_filename,passphrase))
        return cmdResult

    def validateMigration(self):
        binaryCopied= open('/tmp/validateMigration.csv','w')
        good_binaries = self.server.getAllBinaryURIs()
        all_binaries = os.listdir(self.binaryDir)
        encrypt_dir = os.listdir(self.destFolder)
        try:
            for dataresourceid in good_binaries:

                dataresources = good_binaries[dataresourceid]
                remotePass = dataresources[0][3]
                if remotePass is '':
                    add = '[E - NO PASS], %s,%s,%s,%s,' %(dataresources[0][0],dataresources[0][1],dataresources[0][2],dataresources[0][3])
                    print add
                    binaryCopied.write(add+'\n')
                    continue
                for myBin in dataresources:
                    if myBin[3] == remotePass:
                        if myBin[1] != '' and myBin[1] != 'NOT PRESENT' and myBin[1] != '0':
                            if myBin[1] in encrypt_dir:
                                continue
                            add = '[E - NO STOR], %s,%s,%s,%s,' %(myBin[0],myBin[1],myBin[2],myBin[3])
                            print add
                            binaryCopied.write(add+'\n')
                            continue
                        continue
                    add = '[E - TREE ER], %s,%s,%s,%s,' %(myBin[0],myBin[1],myBin[2],myBin[3])
                    print add
                    binaryCopied.write(add+'\n')

        except Exception,e:
            print e

        binaryCopied.close()



def startEncryption(username, password):

    test = EncryptionMigration(username,password, 'test.physiomespace.com','/scs/app/www/Storage/')
    test.encryptBinary()
    test.validateMigration()

def validateEncryption(username, password):

    test = EncryptionMigration(username,password, 'next.physiomespace.com','/scs/app/www/Storage/')
    test.validateMigration()

def testOneData(dataresource, username, password):

    test = EncryptionMigration(username,password, 'test.physiomespace.com','/scs/app/www/Storage/')
    test.encryptBinary(dataresource)

def testOneData2(dataresource, username, password):

    test = EncryptionMigration(username,password, 'www.physiomespace.com','/scs/app/www/Storage/')
    test.encryptBinary(dataresource)

##REPODOWNLOAD

def findSubNode(dom, tag, name, val):
    for nod in dom.iter(tag):
        if nod.get(name) == val:
            return nod[0][0].text
    return ''


def setNodeTextValue(dom, tag, name, tagVal, nodeVal):
    for nod in dom.iter():
        if nod.tag == tag and nod.get(name) == tagVal:
            nod[0][0].text = nodeVal


class DataResource(object):

    def __init__(self, username, pwd, dataresource_id, repository_id='', ps_url='www.physiomespace.com'):

        self.username = username
        self.pwd = pwd
        self.id = dataresource_id
        self.ps_url = ps_url
        self.title = ''
        self.repository_id = repository_id or username

        self.url = 'https://%s/Members/%s/%s' % (self.ps_url, self.repository_id, self.id)
        self.proxy = ServerProxy('https://%s:%s@%s/Members/%s/%s' % (self.username, self.pwd, self.ps_url, self.repository_id, self.id), allow_none=True)

        self.xml = None
        self.children = []
        self.binary_uri = ''
        self.description = ''
        self.passphrase = ''
        self.filename = ''
        self.vmetype = ''
        self.passphrase = ''
        self.root = False
        self.permissions = []

        self.update()

    def update(self):
        self.xml = etree.fromstring(self.proxy.getRawFile())

        self.title = self.xml.get('Name', 'No name')
        self.description = self.proxy.description()
        self.passphrase = self.proxy.getPassphrase()
        self.vmetype = findSubNode(self.xml, "TItem", "Name", "L0000_resource_MAF_VmeType")
        self.root = findSubNode(self.xml, "TItem", "Name", "L0000_resource_MAF_TreeInfo_VmeRootURI") == self.id

        self.binary_uri = findSubNode(self.xml, "TItem", "Name", "L0000_resource_data_Dataset_DatasetURI")
        if self.binary_uri == 'NOT PRESENT':
            self.binary_uri = False
        # find filename
        if self.binary_uri:
            filename = findSubNode(self.xml, "TItem", "Name", "EXTDATA_FILENAME")
            ext = findSubNode(self.xml, "TItem", "Name", "EXTDATA_EXTENSION")

            if filename and ext:
                self.filename = "%s.%s" % (filename, ext)
            else:
                # look into datavector node, if present
                datavector = self.xml.find(".//DataVector")
                if datavector is not None:
                    if datavector.get('ArchiveFileName', ''):
                        self.filename = datavector.get('ArchiveFileName')
                    else:
                        self.filename = datavector.find(".//VItem//URL").text

        children_ids = findSubNode(self.xml, "TItem", "Name", "L0000_resource_MAF_TreeInfo_VmeChildURI1")
        if children_ids != "This tag will be filled during the upload process":
            children_ids = children_ids.split()
            for children_id in children_ids:
                self.children.append(DataResource(self.username, self.pwd, children_id, self.repository_id, self.ps_url))
        else:
            self.children = []

        # permissions only for roots
        if self.root:
            self.get_permission_map()

    def pretty_print(self, tab=' '):
        buff = tab + self.title + "(%s, %s)" % (self.binary_uri, self.filename) + '\n'
        for c in self.children:
            buff += c.pretty_print(tab=tab+' ')
        return buff

    def get_permission_map(self):
        # maybe not the best way, surely the fastest

        # rolemap is a list of tuple like: (('AuthenticatedUsers', ('Reader',)), ('IOR_LTM', ('Owner',)), ('mbalasso', ('Owner',)))
        infos = self.proxy.getParentDataResourceInfo()
        self.permissions = infos.get('rolemap', [])

    def download(self, output_dir):

        # TODO! controlla il file di migrazione dell'encryption: il size nel file xml deve essere aggiornato dopo la decriptazione?
        # E il checksum? Deve essere aggiornato anch'esso?

        for child in self.children:
            child.download(output_dir)

        if not self.binary_uri:
            return False

        cwd = os.getcwd()
        os.chdir(output_dir)

        os.chdir(cwd)

        if has_binary and ENCRYPTION:
            # decryptq
            subprocess.call([BOTAN_APP, 'D', os.path.join(output_dir, self.binary_uri), os.path.join(output_dir, self.filename), self.passphrase])
            # delete encrypted
            os.remove(os.path.join(output_dir, self.binary_uri))
            return True

        return False

    def publish_to_vphshare(self):
        # TODO! Rememeber the semantic delirium :-)
        # DictionaryTool on physiomespace is here: https://www.physiomespace.com/ps_dictionarytool/view
        pass


class PrivateRepository():

    def __init__(self, username, pwd, repository_id='', ps_url='www.physiomespace.com'):

        self.username = username
        self.pwd = pwd
        self.ps_url = ps_url
        self.repository_id = repository_id or username

        self.url = 'https://%s/Members/%s' % (self.ps_url, self.repository_id)
        self.proxy = ServerProxy('https://%s:%s@%s/Members/%s' % (self.username, self.pwd, self.ps_url, self.repository_id), allow_none=True)

        self.sandbox = []
        self.dashboard = []

        self.update()

    def update(self):
        sandbox = self.proxy.listSandbox()
        # self.dashboard = self.proxy.listDashboard()

        for title, dataresource_id in sandbox:
            print "-- Downloading tree xmls for %s (%s)" % (title, dataresource_id)
            self.sandbox.append(DataResource(self.username, self.pwd, dataresource_id, self.repository_id))
            print "-- OK"

    def download(self, output_dir):
        for dataresource in self.sandbox:
            print "-- Downloading binaries for %s (%s)" % (dataresource.title, dataresource.id)
            data_directory = os.path.join(output_dir, dataresource.id)
            if not os.path.exists(data_directory):
                os.makedirs(data_directory)
            dataresource.download(data_directory)
            print "-- OK"



if __name__ == "__main__":
    test = EncryptionMigration('','', 'test.physiomespace.com','/scs/app/www/Storage/')
    test.encryptBinary()







