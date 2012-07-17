"""
mod_auth_tkt style cookie authentication
========================================

This module implements the session cookie format from mod_auth_tkt_. For
compatability with other implementations, pass ``mod_auth_tkt=True`` to the
``createTicket`` and ``validateTicket`` functions. This invokes the MD5_ based
double hashing scheme in the original mod_auth_tkt. If such compatability is
not required, a more secure HMAC_ SHA-256_ cryptographic hash may be used
(which is the default.)

.. _mod_auth_tkt: http://www.openfusion.com.au/labs/mod_auth_tkt/
.. _mod_auth_pubtkt: https://neon1.net/mod_auth_pubtkt/index.html
.. _MD5: http://en.wikipedia.org/wiki/MD5
.. _HMAC: http://en.wikipedia.org/wiki/HMAC
.. _SHA-256: http://en.wikipedia.org/wiki/SHA-256


Example
-------

This is a python doctest, you may run this file to execute the test with the
command `python tktauth.py`. No output indicates success.

The protocol depends on a secret string shared between servers. From time to
time this string should be changed, so store it in a configuration file.

  >>> SECRET = 'abcdefghijklmnopqrstuvwxyz0123456789'

The tickets are only valid for a limited time. Here we will use 12 hours

  >>> TIMEOUT = 12*60*60


Cookie creation
---------------

We have a user with the following id:

  >>> userid = 'jbloggs'

We first set the validuntil that the user will log out, for the purposes of this
test 2008-07-22 11:00 + 12h:

  >>> validuntil = 1216720800 + DEFAULT_TIMEOUT

We will create a mod_auth_tkt compatible ticket. In the simplest case no extra
data is supplied.

  >>> tkt = createTicket( userid, SECRET, validuntil=validuntil, mod_auth_tkt=True)
  >>> tkt
  'c7c7300ac5cf529656444123aca345294885afa0jbloggs!'

The cookie itself should be base64 encoded. We will use the built-in Cookie
module here, your web framework may supply it's own mechanism.

  >>> import Cookie, binascii
  >>> cookie = Cookie.SimpleCookie()
  >>> cookie['auth_tkt'] = binascii.b2a_base64(tkt).strip()
  >>> print cookie
  Set-Cookie: auth_tkt=YzdjNzMwMGFjNWNmNTI5NjU2NDQ0MTIzYWNhMzQ1Mjk0ODg1YWZh...


Cookie validation
-----------------

First the ticket has to be read from the cookie and unencoded:

  >>> tkt = binascii.a2b_base64(cookie['auth_tkt'].value)
  >>> tkt
  'c7c7300ac5cf529656444123aca345294885afa0jbloggs!'

Splitting the data reveals the contents (note the unicode output):

  >>> splitTicket(tkt)
  ('c7c7300ac5cf529656444123aca34529', u'jbloggs', (), u'', 1216720800)

We will validate it an hour after it was created:

  >>> NOW = timestamp + 60*60
  >>> data = validateTicket( tkt, SECRET,  now=NOW, mod_auth_tkt=True)
  >>> data is not None
  True

After the timeout the ticket is no longer valid

  >>> LATER = NOW + TIMEOUT
  >>> data = validateTicket( tkt, SECRET, now=LATER, mod_auth_tkt=True)
  >>> data is not None
  False


Tokens and user data
--------------------

The format allows for optional user data and tokens. We will store the user's
full name in the user data field. We are not yet using tokens, but may do so in
the future.

  >>> user_data = 'Joe Bloggs'
  >>> tokens = ['foo', 'bar']
  >>> tkt = createTicket( userid, SECRET, tokens, user_data, validuntil=validuntil, mod_auth_tkt=True)
  >>> tkt
  'eea3630e98177bdbf0e7f803e1632b7e4885afa0jbloggs!foo,bar!Joe Bloggs'
  >>> cookie['auth_tkt'] = binascii.b2a_base64(tkt).strip()
  >>> print cookie
  Set-Cookie: auth_tkt=ZWVhMzYzMGU5ODE3N2JkYmYwZTdmODAzZTE2MzJiN2U0ODg1YWZh...
  >>> data = validateTicket( tkt, SECRET,  now=NOW, mod_auth_tkt=True)
  >>> data
  ('eea3630e98177bdbf0e7f803e1632b7e', u'jbloggs', (u'foo', u'bar'), u'Joe Bloggs', 1216720800)


Using the more secure hashing scheme
------------------------------------

The HMAC SHA-256 hash must be packed raw to fit into the first 32 bytes.

  >>> tkt = createTicket( userid,SECRET, validuntil=validuntil)
  >>> tkt
  '\xf3\x08\x98\x99\x83\xb0;\xef\x95\x94\xee...\xbe\xf6X\x114885afa0jbloggs!'
  >>> data = validateTicket(tkt, SECRET, now=NOW)
  >>> data is not None
  True

++++++++++++++++++++++++++++++++++++++
MOD_AUTH_PUBTKT is a method to sign ticket with DSA or RSA key pair.
++++++++++++++++++++++++++++++++++++++
@author: Alfredo Saglimbeni (a.saglimbeni@scsitaly.com)

Mod_auth_pubtkt is a module that authenticates a user based on a cookie
with a ticket that has been issued by a central login server and digitally signed
using either RSA or DSA. This means that only the trusted login server has the private key
required to generate tickets, while web servers only need the corresponding public key to verify them.

#With last commit , function support this functionality in the createticket and validateticket function
there is new flag to activate new feature. When you use ticket signature you don't need  to set SECRET  variable. It is ignored.
In this feature , the ticket change her structure in this way:

 "userID=;validuntil=;clientIp=;token='';user_data='';sign=''"
 example:
 uid=testuser;validuntil=1342568679;cip=0.0.0.0;tokens=role1,role2;udata=testuser,Test User,nomail@mail.com,,,;sig=MCwCFCWdUT71tdZfgFqmNK6BMIeq1qNiAhRFMzfjF7dZV1W+rqd97sRdISddMA==




Configuration
+++++++++++++
--> BE CAREFUL! Please, if use this module in your project, generate new keys and replace them into ./keys directory !!!
Generating a key pair:
!Save the key pair into ./keys directory!
From the terminal:
DSA:
# openssl dsaparam -out dsaparam.pem 1024
# openssl gendsa -out privkey_DSA.pem dsaparam.pem
# openssl dsa -in privkey_DSA.pem -out pubkey_DSA.pem -pubout
The dsaparam.pem file is not needed anymore after key generation and can safely be deleted.

RSA:
# openssl genrsa -out privkey_DSA.pem 1024
# openssl rsa -in privkey_DSA.pem -out pubkey_DSA.pem -pubout



"""

from socket import inet_aton
from struct import pack
import hashlib
import hmac
import time
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
#from Crypto.PublicKey import RSA, DSA
import base64
import os

###IMPORT FOR MOD_AUTHPUBTKT###
from M2Crypto import RSA, DSA

## DEFAULT CONFIGURATION
DEFAULT_TIMEOUT= 12*60*60
########################

###########################
#### MOD_AUTH_PUBTKT ######
###########################

class TicketParseError(Exception):
    """Base class for all ticket parsing errors"""

    def __init__(self, ticket, msg=''):
        self.ticket = ticket
        self.msg = msg

    def __str__(self):
        return 'Ticket parse error: %s  (%s)' % (self.msg, self.ticket)


class BadTicket(TicketParseError):
    """Exception raised when a ticket has invalid format"""

    def __init__(self, ticket, msg=''):
        if not msg:
            msg = 'Invalid ticket format'
        super(self.__class__, self).__init__(ticket, msg)


class BadSignature(TicketParseError):
    """Exception raised when a signature verification is failed"""

    def __init__(self, ticket):
        super(self.__class__, self).__init__(ticket, 'Bad signature')

def verify_sig(pubkey, data, sig):
    """Verify ticket signature.

    Returns False if ticket is tampered with and True if ticket is good.

    Arguments:

    ``pubkey``:
        Public key object. It must be M2Crypto.RSA.RSA_pub or M2Crypto.DSA.DSA_pub instance

    ``data``:
        Ticket string without signature part.

    ``sig``:
        Ticket's sig field value.

    """
    sig = base64.b64decode(sig)
    dgst = hashlib.sha1(data).digest()
    if isinstance(pubkey, RSA.RSA_pub):
        try:
            pubkey.verify(dgst, sig, 'sha1')
        except RSA.RSAError:
            return False
        return True
    elif isinstance(pubkey, DSA.DSA_pub):
        return not not pubkey.verify_asn1(dgst, sig)
    else:
        raise ValueError('Unknown key type: %s' % pubkey)

def calculate_sign(privkey, data):
    """Calculates and returns ticket's signature.

    Arguments:

    ``privkey``:
       Private key object. It must be M2Crypto.RSA.RSA or M2Crypto.DSA.DSA instance.

    ``data``:
       Ticket string without signature part.

    """
    dgst = hashlib.sha1(data).digest()
    if isinstance(privkey, RSA.RSA):
        sig = privkey.sign(dgst, 'sha1')
        sig = base64.b64encode(sig)
    elif isinstance(privkey, DSA.DSA):
        sig = privkey.sign_asn1(dgst)
        sig = base64.b64encode(sig)
    else:
        raise ValueError('Unknonw key type: %s' % privkey)

    return sig



def parse_pub_ticket(ticket, pubkey, verify_sig=verify_sig):
    """Parse and verify auth_pubtkt ticket.

    Returns dict with ticket's fields.

    ``BadTicket`` and ``BadSignature`` exceptions can be raised
    in case of invalid ticket format or signature verification failure.

    Arguments:

    ``ticket``:
        Ticket string value.

    ``pubkey``:
        Public key object. It must be M2Crypto.RSA.RSA_pub or M2Crypto.DSA.DSA_pub instance

    ``verify_sig``:
        Function which perform signature verification. By default verify_sig function from this module is used.
        This argument is needed for testing purposes only.

    """

    i = ticket.rfind(';')
    sig = ticket[i+1:]
    if sig[:4] != 'sig=':
        raise BadTicket(ticket)
    sig = sig[4:]
    data = ticket[:i]

    if not verify_sig(pubkey, data, sig):
        raise BadSignature(ticket)

    try:
        fields = dict(f.split('=', 1) for f in data.split(';'))
    except ValueError:
        raise BadTicket(ticket)

    if 'uid' not in fields:
        raise BadTicket(ticket, 'uid field required')

    if 'validuntil' not in fields:
        raise BadTicket(ticket, 'validuntil field required')

    try:
        fields['validuntil'] = int(fields['validuntil'])
    except ValueError:
        raise BadTicket(ticket, 'Bad value for validuntil field')

    if 'tokens' in fields:
        tokens = fields['tokens'].split(',')
        if tokens == ['']:
            tokens = []
        fields['tokens'] = tokens
    else:
        fields['tokens'] = []

    if 'udata' in fields:
        udata = fields['udata'].split(',')
        if udata == ['']:
            udata = []
        fields['udata'] = udata
    else:
        fields['tokens'] = []

    if 'graceperiod' in fields:
        try:
            fields['graceperiod'] = int(fields['graceperiod'])
        except ValueError:
            raise BadTicket(ticket, 'Bad value for graceperiod field')

    return fields


def create_pub_ticket(privkey, uid, validuntil, ip=None, tokens=(),
                  udata=(), graceperiod=None, extra_fields = ()):
    """Returns signed mod_auth_pubtkt ticket.

    Mandatory arguments:

    ``privkey``:
       Private key object. It must be M2Crypto.RSA.RSA or M2Crypto.DSA.DSA instance.

    ``uid``:
        The user ID. String value 32 chars max.

    ``validuntil``:
        A unix timestamp that describe when this ticket will expire. Integer value.

    Optional arguments:

    ``ip``:
       The IP address of the client that the ticket has been issued for.

    ``tokens``:
       List of authorization tokens.

    ``udata``:
       Misc user data.

    ``graceperiod``:
        A unix timestamp after which GET requests will be redirected to refresh URL.

    ``extra_fields``:
        List of (field_name, field_value) pairs which contains addtional, non-standard fields.
    """

    v = 'uid=%s;validuntil=%d' % (uid, validuntil)
    if ip:
        v += ';cip=%s' % ip
    if tokens:
        v += ';tokens=%s' % ','.join(tokens)
    if graceperiod:
        v += ';graceperiod=%d' % graceperiod
    if udata:
        v += ';udata=%s' % ','.join(udata)
    for k,fv in extra_fields:
        v += ';%s=%s' % (k,fv)
    v += ';sig=%s' % calculate_sign(privkey, v)
    return v

###########################
###//END:MOD_AUTH_PUBTKT###
###########################

#######################
#### MOD_AUT_TKT ######
#######################

def mod_auth_tkt_digest(secret, data1, data2):
    digest0 = hashlib.md5(data1 + secret + data2).hexdigest()
    digest = hashlib.md5(digest0 + secret).hexdigest()
    return digest


def createTicket( userid, secret=None, tokens=(), user_data=(), ip='0.0.0.0', validuntil=None, encoding='utf8', mod_auth_tkt=True, mod_auth_pubtkt=False, signType='DSA'):
    """
    Create Ticket from given data.

    Arguments:
            secret (string) : secret.\n
            userid (string) : The user unique identifier.\n
            tokens (tupla) : Permission for Given user.\n
            user_data (tupla) : User's infromations.\n
            ip : sender ip.\n
            validuntil : ticket validate until (unix timestamp) .\n
            encoding : encoding\n
            mod_auth_tkt : if true encode ticket with secret key.\n
            mod_auth_pubtkt : if true , support ticket sign with RSA keys.
            signType : if mod_auth_pubtkt is active this flag select what type of signature to use, RSA or DSA

    Return:
            Ticket (string) : Resulting ticket.\n

    """
    if validuntil is None:
        validuntil = int(time.time()) + DEFAULT_TIMEOUT

    userid = userid.encode(encoding)
    if mod_auth_pubtkt:
        #LOAD  KEY
        if signType == 'RSA':
            key = RSA.load_key(os.path.abspath(os.path.dirname(__file__))+'/keys/privkey_RSA.pem')
        else:
            key = DSA.load_key(os.path.abspath(os.path.dirname(__file__))+'/keys/privkey_DSA.pem')
        ticket=create_pub_ticket(key,userid,validuntil,ip,tokens,user_data) #da inserire il graceperiod
    else:

        ##OLD VERSION WITHOUT DSA SIGN
        token_list = ','.join(tokens).encode(encoding)

        user_list = ','.join(user_data).encode(encoding)

        # ip address is part of the format, set it to 0.0.0.0 to be ignored.
        # inet_aton packs the ip address into a 4 bytes in network byte order.
        # pack is used to convert timestamp from an unsigned integer to 4 bytes
        # in network byte order.
        data1 = inet_aton(ip) + pack("!I", validuntil)
        data2 = '\0'.join((userid, token_list, user_list))
        if mod_auth_tkt:
            digest = mod_auth_tkt_digest(secret, data1, data2)
        else:
            # a sha256 digest is the same length as an md5 hexdigest
            digest = hmac.new(secret, data1+data2, hashlib.sha256).digest()

        # digest + timestamp as an eight character hexadecimal + userid + !
        ticket = "%s%08x%s!" % (digest, validuntil, userid)

        if tokens:
            ticket += token_list + '!'
        if user_data:
            ticket += user_list

    return ticket

def splitSignedTicket(ticket, encoding='utf8'):


    parts = ticket.decode(encoding).split("!")

    timestamp , userid, cip, token_list, user_data, signature = parts

    if len(user_data)>0:
        user_data = tuple(user_data.split(','))
    if len(token_list)>0:
        tokens = tuple(token_list.split(','))
    else:
        raise ValueError

    return ( timestamp , userid, cip, tokens, user_data, signature)

def splitTicket(ticket, encoding='utf8'):
    digest = ticket[:32]
    val = ticket[32:40]
    if not val:
        raise ValueError
    timestamp = int(val, 16) # convert from hexadecimal+

    parts = ticket[40:].decode(encoding).split("!")

    if len(parts) == 2:
        userid, user_data = parts
        tokens = ()
        if len(user_data)>0:
            user_data = tuple(user_data.split(','))

    elif len(parts) == 3:
        userid, token_list, user_data = parts
        tokens = tuple(token_list.split(','))
        user_data = tuple(user_data.split(','))
    else:
        raise ValueError

    return (digest, userid, tokens, user_data, timestamp)


def validateTicket( ticket, secret=None , ip='0.0.0.0', now=None, encoding='utf8', mod_auth_tkt=True, mod_auth_pubtkt=False, signType='DSA'):
    """
    To validate, a new ticket is created from the data extracted from cookie
    and the shared secret. The two digests are compared and timestamp checked.
    Successful validation returns (digest, userid, tokens, user_data, timestamp).
    On failure, return None.
    Arguments:
                secret (string) : secret.\n
                ticket: given ticket.\n
                ip : sender ip.\n
                now: now timestamp.\n
                encoding : encoding.\n
                mod_auth_tkt : if true encode ticket with secret key.\n
                mod_auth_pubtkt : if true , support ticket sign with RSA keys.
                signType : if mod_auth_pubtkt is true this flag select what type of signature to use , RSA or DSA

    Return:
                Ticket (string) : Resulting ticket.
    """
    try:
        if mod_auth_pubtkt:
        #LOAD  KEY

            if signType == 'RSA':
                key = RSA.load_pub_key(os.path.abspath(os.path.dirname(__file__))+'/keys/pubkey_RSA.pem')
            else:
                key = DSA.load_pub_key(os.path.abspath(os.path.dirname(__file__))+'/keys/pubkey_DSA.pem')

            parsed_ticket = parse_pub_ticket(ticket, key)
            ( validuntil , userid, cip, token_list, user_data) = parsed_ticket['validuntil'],  parsed_ticket['uid'], parsed_ticket['cip'] ,parsed_ticket['tokens'] ,parsed_ticket['udata']

            if now is None:
                now = time.time()
            if int(validuntil) > now:
                return '',userid,token_list,user_data,validuntil
        else:
            (digest, userid, tokens, user_data, validuntil) = data = splitTicket(ticket)
            new_ticket = createTicket(userid, secret , tokens, user_data, ip, validuntil, encoding, mod_auth_tkt, mod_auth_pubtkt , signType)
            if new_ticket[:32] == digest:

                if now is None:
                    now = time.time()
                if validuntil > now:
                    return data

    except ValueError:
        return None

    return None

#######################
## //END:MOD_AUT_TKT ##
#######################


# doctest runner
def _test():
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)

if __name__ == "__main__":
    _test()
