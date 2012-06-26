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

We first set the timestamp that the user logged in, for the purposes of this
test 2008-07-22 11:00:

  >>> timestamp = 1216720800

We will create a mod_auth_tkt compatible ticket. In the simplest case no extra
data is supplied.

  >>> tkt = createTicket( userid, SECRET, timestamp=timestamp, mod_auth_tkt=True)
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
  >>> data = validateTicket( tkt, SECRET, timeout=TIMEOUT, now=NOW, mod_auth_tkt=True)
  >>> data is not None
  True

After the timeout the ticket is no longer valid

  >>> LATER = NOW + TIMEOUT
  >>> data = validateTicket( tkt, SECRET, timeout=TIMEOUT, now=LATER, mod_auth_tkt=True)
  >>> data is not None
  False


Tokens and user data
--------------------

The format allows for optional user data and tokens. We will store the user's
full name in the user data field. We are not yet using tokens, but may do so in
the future.

  >>> user_data = 'Joe Bloggs'
  >>> tokens = ['foo', 'bar']
  >>> tkt = createTicket( userid, SECRET, tokens, user_data, timestamp=timestamp, mod_auth_tkt=True)
  >>> tkt
  'eea3630e98177bdbf0e7f803e1632b7e4885afa0jbloggs!foo,bar!Joe Bloggs'
  >>> cookie['auth_tkt'] = binascii.b2a_base64(tkt).strip()
  >>> print cookie
  Set-Cookie: auth_tkt=ZWVhMzYzMGU5ODE3N2JkYmYwZTdmODAzZTE2MzJiN2U0ODg1YWZh...
  >>> data = validateTicket( tkt, SECRET, timeout=TIMEOUT, now=NOW, mod_auth_tkt=True)
  >>> data
  ('eea3630e98177bdbf0e7f803e1632b7e', u'jbloggs', (u'foo', u'bar'), u'Joe Bloggs', 1216720800)


Using the more secure hashing scheme
------------------------------------

The HMAC SHA-256 hash must be packed raw to fit into the first 32 bytes.

  >>> tkt = createTicket( userid,SECRET, timestamp=timestamp)
  >>> tkt
  '\xf3\x08\x98\x99\x83\xb0;\xef\x95\x94\xee...\xbe\xf6X\x114885afa0jbloggs!'
  >>> data = validateTicket(tkt, SECRET, timeout=TIMEOUT, now=NOW)
  >>> data is not None
  True

MOD_AUTH_PUBTKT is a method to sign ticket with DSA or RSA key pair.
------------------------------------
Mod_auth_pubtkt is a module that authenticates a user based on a cookie
with a ticket that has been issued by a central login server and digitally signed
using either RSA or DSA. This means that only the trusted login server has the private key
required to generate tickets, while web servers only need the corresponding public key to verify them.

#With last commit , function support this functionality in the createticket and validateticket function
there is new flag to activate new feature. When you use ticket signature you don't need  to set SECRET  variable. It is ignored.
In this feature , the ticket change her structure in this way:

 "timestamp!userid!clientIp!token!user_data!sign"
 example:
 1340699421!testuser!0.0.0.0!developer!testuser,Test User,test@mysite.com,,ITALY,35012!LJTzocHKFenS+y3O+2Upt1Jp+V+emyNUdQe8PasgvrTXgAD8BAJnoTdJU80m/4AFDA+hjwCtXY99UlIij1zeDFSW1o+kj914CKQgJWW2LwXTDljUufab/4K6KXLZA7+YMZLsPU3/UzaRgy8FZgRkFxcFsRLdD8/Y5/ZiQ7UZjFQ=



Configuration
+++++++++++++
Generating a key pair:
!Save the key pair into ./keys directory!
From the terminal:
DSA:
# openssl dsaparam -out dsaparam.pem 1024
# openssl gendsa -out privkey.pem dsaparam.pem
# openssl dsa -in privkey.pem -out pubkey.pem -pubout
The dsaparam.pem file is not needed anymore after key generation and can safely be deleted.

RSA:
# openssl genrsa -out privkey.pem 1024
# openssl rsa -in privkey.pem -out pubkey.pem -pubout



"""

from socket import inet_aton
from struct import pack
import hashlib
import hmac
import time
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import base64
import os

def mod_auth_tkt_digest(secret, data1, data2):
    digest0 = hashlib.md5(data1 + secret + data2).hexdigest()
    digest = hashlib.md5(digest0 + secret).hexdigest()
    return digest

def verify_sig(pubkey, data, signature):
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
    h = SHA.new(data)
    verifier = PKCS1_v1_5.new(pubkey)
    signature=base64.b64decode(signature)
    if verifier.verify(h, signature):
        return True
    return False

def calculate_sign(privkey, data):
    """Calculates and returns ticket's signature.

    Arguments:

    ``privkey``:
       Private key object. It must be M2Crypto.RSA.RSA or M2Crypto.DSA.DSA instance.

    ``data``:
       Ticket string without signature part.

    """

    h = SHA.new(data)
    signer = PKCS1_v1_5.new(privkey)
    signature = signer.sign(h)
    signature = base64.b64encode(signature)
    return signature


def createTicket( userid, secret=None, tokens=(), user_data=(), ip='0.0.0.0', timestamp=None, encoding='utf8', mod_auth_tkt=True, mod_auth_pubtkt=False):
    """
    Create Ticket from given data.

    Arguments:
            secret (string) : secret.\n
            userid (string) : The user unique identifier.\n
            tokens (tupla) : Permission for Given user.\n
            user_data (tupla) : User's infromations.\n
            ip : sender ip.\n
            timestamp : ticket timestamp.\n
            encoding : encoding\n
            mod_auth_tkt : if true encode ticket with secret key.\n
            mod_auth_pubtkt : if true , support ticket sign with RSA keys.

    Return:
            Ticket (string) : Resulting ticket.\n

    """
    if timestamp is None:
        timestamp = int(time.time())

    userid = userid.encode(encoding)
    token_list = ','.join(tokens).encode(encoding)

    user_list = ','.join(user_data).encode(encoding)

    # ip address is part of the format, set it to 0.0.0.0 to be ignored.
    # inet_aton packs the ip address into a 4 bytes in network byte order.
    # pack is used to convert timestamp from an unsigned integer to 4 bytes
    # in network byte order.
    data1 = inet_aton(ip) + pack("!I", timestamp)
    data2 = '\0'.join((userid, token_list, user_list))

    if mod_auth_pubtkt:

        ticket = str(timestamp) + "!"+ userid + "!" + ip +"!"
        ticket += token_list + '!'
        ticket += user_list + '!'

        #LOAD RSA KEY
        key = RSA.importKey(open(os.path.abspath(os.path.dirname(__file__))+'/keys/privkey.der').read())

        sign = calculate_sign(key, ticket)
        ticket += sign
    else:
        if mod_auth_tkt:
            digest = mod_auth_tkt_digest(secret, data1, data2)
        else:
            # a sha256 digest is the same length as an md5 hexdigest
            digest = hmac.new(secret, data1+data2, hashlib.sha256).digest()

        # digest + timestamp as an eight character hexadecimal + userid + !
        ticket = "%s%08x%s!" % (digest, timestamp, userid)

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


def validateTicket( ticket, secret=None , ip='0.0.0.0', timeout=0, now=None, encoding='utf8', mod_auth_tkt=True,mod_auth_pubtkt=False):
    """
    To validate, a new ticket is created from the data extracted from cookie
    and the shared secret. The two digests are compared and timestamp checked.
    Successful validation returns (digest, userid, tokens, user_data, timestamp).
    On failure, return None.
    Arguments:
                secret (string) : secret.\n
                ticket: given ticket.\n
                ip : sender ip.\n
                timestamp : ticket timestamp.\n
                now: now timestamp.\n
                encoding : encoding.\n
                mod_auth_tkt : if true encode ticket with secret key.\n
                mod_auth_pubtkt : if true , support ticket sign with RSA keys.

    Return:
                Ticket (string) : Resulting ticket.
    """
    try:
        if mod_auth_pubtkt:
            ( timestamp , userid, cip, token_list, user_data, signature) = data = splitSignedTicket(ticket)
            key = RSA.importKey(open(os.path.abspath(os.path.dirname(__file__))+'/keys/pubkey.der').read())
            s_tokens = ",".join(token_list).encode(encoding)
            s_user_data = ",".join(user_data).encode(encoding)
            if not verify_sig(key,'!'.join((timestamp , userid, cip, s_tokens, s_user_data,'')).encode(encoding),data[5]):
                return None
            if now is None:
                now = time.time()
            if int(timestamp) + timeout > now:
                return ('',userid,token_list,user_data,timestamp)
        else:
            (digest, userid, tokens, user_data, timestamp) = data = splitTicket(ticket)
            new_ticket = createTicket(userid, secret , tokens, user_data, ip, timestamp, encoding, mod_auth_tkt, mod_auth_pubtkt)
            if new_ticket[:32] == digest:
                if not timeout:
                    return data
                if now is None:
                    now = time.time()
                if timestamp + timeout > now:
                    return data

    except ValueError:
        return None

    return None



# doctest runner
def _test():
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)

if __name__ == "__main__":
    _test()
