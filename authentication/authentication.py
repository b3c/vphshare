__author__ = """Alfredo Saglimbeni <a.saglimbeni@cineca.it>"""
__docformat__ = 'plaintext'

"""
.. module:: authentication_bt

.. moduleauthor:: Alfredo Saglimbeni <a.saglimbeni@cineca.it>

"""

import time
from flask import Flask, abort
from flask import request, session, redirect, url_for, render_template, flash

try:
    from flaskext.xmlrpc import XMLRPCHandler
except ImportError, e:
    from flask.ext.xmlrpc import XMLRPCHandler
try:
    from flaskext.login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
except ImportError, e:
    from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

from dbconnection import usersTable, usersList
from mod_auth import SignedTicket, Ticket
from xmlrpclib import Server
import binascii
import base64
import os
import json
import requests
from datetime import timedelta

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
MOD_AUTH_PRIVKEY = os.path.join(PROJECT_ROOT, 'keys/privkey_DSA.pem')
MOD_AUTH_PUBKEY = os.path.join(PROJECT_ROOT, 'keys/pubkey_DSA.pem')
TICKET = SignedTicket(MOD_AUTH_PUBKEY, MOD_AUTH_PRIVKEY)

CREDENTIAL_MANAGER_URL = "www.biomedtown.org"
TIMEOUT = 12 * 60 * 60  # 12h
####################### USERS  ###########################


class User(UserMixin):
    """ *User* Object
    """

    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active


USERS = {}
index = 1
for u in usersList:
    USERS[index] = User(u['name'], index)
    index += 1

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())

################### FLASK CONFIGURATION ####################
app = Flask(__name__)

# Configuration Values
app.config.update(
    DEBUG=True,
    SECRET_KEY='09b63a0aa787db09b73c675b1e04224a',
    TIME_OUT=12 * 60 * 60,  # 12h
    MASTERINTERFACE_VALIDATE_TKT_SERVICE="https://portal.vph-share.eu/validatetkt/?ticket=%s",
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=TIMEOUT)
)

#TICKET = Ticket(app.config['SECRET_KEY'])

# flask LoginMagers
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"

############################################################

############################################################################
# connect xmlrpc handler to app
handler = XMLRPCHandler('api')
handler.connect(app, '/api')


@login_manager.user_loader
def load_user(id):
    """ *load_user* method
    
        This method should take the unicode ID of a user
        and return the corresponding user object.
    """

    return USERS.get(int(id))


@app.route("/")
def index():
    """ *index* method 
        
        Return rendering to index page.
    """
    return redirect(url_for("login"))


@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    """ *login* method

        This method get username and password from request form and validate it.
        If they are valid create a ticket for the current user using a SECRET_KEY shared with plone. After
        is create a cookie with the ticket and domain linked to came_from.

        Return response.
    """
    import urllib
    if request.method == 'GET':
        username = request.args.get("username")
        password = urllib.unquote(request.args.get("password"))
        domain = request.args.get("domain", "")
    elif request.method == 'POST':
        username = request.form['username']
        password = urllib.unquote(request.form['password'])
        domain = request.form.get("domain", "")
    else:
        return abort(403)

    if not username and not password:
        return abort(403)

    else:
        validate_user = validate_username(username)
        validate_bt = validate_to_biomedtown(username, password)

        if validate_bt is False:
            return abort(403)
        else:
            if validate_user is not True:
                ins = usersTable.insert().values(name=username).execute()
                lastid = ins.last_inserted_ids()[0]
                USERS[lastid] = User(username, lastid)
                USER_NAMES[username] = USERS[lastid]

            # user_data = [ud for ud in validate_bt.values()]
            user_data = [validate_bt['nickname'],
                         validate_bt['fullname'],
                         validate_bt['email'],
                         validate_bt['language'],
                         validate_bt['country'],
                         validate_bt['postcode']
            ]

            cip = str(request.remote_addr)
            validuntil = int(time.time()) + TIMEOUT
            ticket = TICKET.createTkt(validate_bt['nickname'], tokens=(), user_data=user_data, cip=cip, validuntil=validuntil)

            #ticket = createTicket(app.config['SECRET_KEY'], request.form['username'], tokens=(), user_data=user_data)
            ticket_b64 = binascii.b2a_base64(ticket).rstrip()

            if str(domain).lower().count("vphshare"):
                # we have to retrive the user roles from the MI
                validate_tkt_response = requests.get(
                    app.config['MASTERINTERFACE_VALIDATE_TKT_SERVICE'] % ticket_b64,
                    verify = False
                )

                mi_user_data = json.loads(validate_tkt_response.text)
                tokens = mi_user_data.get('role', [])

                ticket = TICKET.createTkt(validate_bt['nickname'], tokens=tokens, user_data=user_data, cip=cip, validuntil=validuntil)
                ticket_b64 = binascii.b2a_base64(ticket).rstrip()

            return app.make_response(ticket_b64)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ *login* method
    
        This method get username and password from request form and validate it.
        If they are valid create a ticket for the current user using a SECRET_KEY shared with plone. After
        is create a cookie with the ticket and domain linked to came_from.
        
        Return response.
    """
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        domain = request.args.get("domain", "")

        if not username and not password:
            return render_template('login.html', error='Insert username and password!')

        else:
            validate_user = validate_username(username)
            validate_bt = validate_to_biomedtown(username, password)

            if validate_bt is False:
                return render_template('login.html', error='Invalid password!', username=username)
            else:
                if validate_user is not True:
                    ins = usersTable.insert().values(name=username).execute()
                    lastid = ins.last_inserted_ids()[0]
                    USERS[lastid] = User(username, lastid)
                    USER_NAMES[username] = USERS[lastid]

                # user_data = [ud for ud in validate_bt.values()]
                user_data = [validate_bt['nickname'],
                             validate_bt['fullname'],
                             validate_bt['email'],
                             validate_bt['language'],
                             validate_bt['country'],
                             validate_bt['postcode']
                ]
                remember = request.form.get("remember", "no") == "yes"
                if login_user(USER_NAMES[username], remember=remember):
                    flash("Logged in!")
                    cip = str(request.remote_addr)
                    validuntil = int(time.time()) + TIMEOUT
                    ticket = TICKET.createTkt(request.form['username'], tokens=(), user_data=user_data, cip=cip,
                                              validuntil=validuntil)

                    #ticket = createTicket(app.config['SECRET_KEY'], request.form['username'], tokens=(), user_data=user_data)
                    ticket_b64 = binascii.b2a_base64(ticket).rstrip()
                    if str(domain).lower().count("vphshare"):
                        # we have to retrive the user roles from the MI
                        validate_tkt_response = requests.get(
                            app.config['MASTERINTERFACE_VALIDATE_TKT_SERVICE'] % ticket_b64,
                            verify = False
                        )

                        mi_user_data = json.loads(validate_tkt_response.text)
                        tokens = mi_user_data.get('role', [])

                        ticket = TICKET.createTkt(validate_bt['nickname'], tokens=tokens, user_data=user_data, cip=cip, validuntil=validuntil)
                        ticket_b64 = binascii.b2a_base64(ticket).rstrip()

                    if request.args.get("came_from"):
                        came_from = request.args.get("came_from")

                        #iif came_from.count("physiomespace"):
                        came_from = "%s?ticket=%s" % ( came_from, ticket_b64 )
                        response = redirect(came_from, 302)
                    else:
                        response = app.make_response(render_template('index.html'))

                    response.set_cookie('bt-tkt', ticket_b64, domain='.biomedtown.org')
                    response.set_cookie('bt-tkt', ticket_b64, domain='.vph-share.eu')

                    return response

    elif request.method == 'GET' and request.args.get("came_from") and current_user.is_authenticated():
        # incoming request from mod auth ticket third party
        ticket_b64 = request.cookies.get('bt-tkt')
        ticket = binascii.a2b_base64(str(ticket_b64))
        domain = request.args.get("domain", "")
        #if validateTicket(app.config['SECRET_KEY'], ticket, timeout=app.config['TIME_OUT']) is not None:
        try:
            cip = str(request.remote_addr)
            if isinstance(TICKET, SignedTicket):
                data = ticket
            else:
                data = ticket, cip
            
            if TICKET.validateTkt(data) is not None:
                flash("Logged in!")
                userid, tocken, userdata, validuntil = TICKET.validateTkt(data)
                validuntil = int(time.time()) + TIMEOUT
                if str(domain).lower().count("vphshare"):
                    # we have to retrive the user roles from the MI
                    validate_tkt_response = requests.get(
                        app.config['MASTERINTERFACE_VALIDATE_TKT_SERVICE'] % ticket_b64,
                        verify = False
                    )

                    mi_user_data = json.loads(validate_tkt_response.text)
                    tokens = mi_user_data.get('role', [])

                    ticket = TICKET.createTkt(userid, tokens=tokens, user_data=userdata, cip=cip, validuntil=validuntil)
                    ticket_b64 = binascii.b2a_base64(ticket).rstrip()

                came_from = request.args.get("came_from")
                target_domain = ".%s" % ".".join(came_from.replace("http://", "").split(".")[1:]).split("/")[0]

                #if came_from.count("physiomespace"):
                came_from = "%s?ticket=%s" % (came_from, ticket_b64)

                # redirect return a response object
                response = redirect(came_from, 307)
                response.set_cookie('bt-tkt', ticket_b64, domain=target_domain)

                return response
            else:
                logout_user()
        except Exception, e:
            pass

    elif not current_user.is_authenticated():
        return render_template("login.html")

    return render_template("login.html")


def rpc_login(username, password):
    """ *login* method
    
        This method get username and password from request form and validate it.
        If they are valid create a ticket for the current user using a SECRET_KEY shared with plone. After
        is create a cookie with the ticket and domain linked to came_from.
        
        Return response.
    """

    if not username and not password:
        return False

    else:
        validate_user = validate_username(username)
        validate_bt = validate_to_biomedtown(username, password)

        if validate_bt is False:
            return False
        else:
            if validate_user is not True:
                ins = usersTable.insert().values(name=username).execute()
                lastid = ins.last_inserted_ids()[0]
                USERS[lastid] = User(username, lastid)
                USER_NAMES[username] = USERS[lastid]
                # user_data = [ud for ud in validate_bt.values()]
            user_data = [validate_bt['nickname'],
                         validate_bt['fullname'],
                         validate_bt['email'],
                         validate_bt['language'],
                         validate_bt['country'],
                         validate_bt['postcode'],
                         validate_bt['institution'],
                         validate_bt['department'],
                         validate_bt['institutionalrole']
            ]

            cip = str(request.remote_addr)
            validuntil = int(time.time()) + TIMEOUT
            ticket = TICKET.createTkt(username, tokens=(), user_data=user_data, cip=cip, validuntil=validuntil)

            #ticket = createTicket(app.config['SECRET_KEY'], username, tokens=(), user_data=user_data)
            ticket_b64 = base64.b64encode(ticket)

            return ticket_b64


@app.route("/logout")
@login_required
def logout():
    """ *logout* method
    
        Call logout_user() and redirect to index page.
    """
    logout_user()
    flash("Logged out.")
    return redirect(url_for("login"))


def validate_to_biomedtown(username, password):
    """ *validate_to_biomedtown* method

        This method check if the password is valid.
        
        Return True or False.
    """
    server = Server('https://%s:%s@%s/portal_towntool/' % (username, password, CREDENTIAL_MANAGER_URL))
    try:
        response = server.authService()
        if response is not False:
            return response
        return False
    except Exception, e:
        return False


def validate_username(username):
    """ *validate_username* method
    
        This method check if exist the username into database.
        
        Return True or False.
    """
    query = usersTable.select(usersTable.c.name == username).execute().first()
    if query is not None:
        return True
    else:
        return False


@app.route("/validate_tkt", methods=["GET", "POST"])
def validate_tkt():
    """ *validate_tkt* method
    """
    try:
        if request.method == 'GET' and request.args.get("ticket"):
            ticket = binascii.a2b_base64(request.args.get("ticket"))
            if ticket is None:
                return "NOT VALID"
                #now = time.time()
                #if app.config['SECRET_KEY'] is not None:
                #ticket_data = validateTicket(app.config['SECRET_KEY'], ticket,
                #    timeout=app.config['TIME_OUT'], now=now, mod_auth_tkt=True)
                #
                #if ticket_data is not None:
                #    return "OK"
            try:
                cip = str(request.remote_addr)
                if isinstance(TICKET, SignedTicket):
                    data = ticket
                else:
                    data = ticket, cip
                ticket_data = TICKET.validateTkt(data)
                return "OK"
            except Exception, e:
                pass
        return "EXPIRE"
    except Exception, e:
        return "NOT VALID"


@app.route("/refresh_tkt", methods=["GET", "POST"])
def refresh_tkt(ticket=None):
    """ *validate_tkt* method
    """
    try:

        if request.method == 'GET':
            ticket = request.args.get("ticket", "")
        elif request.method == 'POST':
            ticket = request.form.get('ticket', "")
        else:
            abort(403)

        if ticket:
            ticket = binascii.a2b_base64(ticket)
            if ticket is None:
                return False

            cip = str(request.remote_addr)
            if isinstance(TICKET, SignedTicket):
                data = ticket
            else:
                data = ticket, cip
            ticket_data = TICKET.validateTkt(data)

            validuntil = int(time.time()) + TIMEOUT
            ticket = TICKET.createTkt(ticket_data[0], ticket_data[1], ticket_data[2], cip=cip, validuntil=validuntil)
            ticket_b64 = base64.b64encode(ticket)
            return ticket_b64

        return False

    except Exception, e:
        return False


def rpc_validate_tkt(ticket=None):
    """ *validate_tkt* method
    """
    try:
        if ticket:
            ticket = binascii.a2b_base64(ticket)
            if ticket is None:
                return False
            now = time.time()
            if app.config['SECRET_KEY'] is not None:
                try:
                    cip = str(request.remote_addr)
                    if isinstance(TICKET, SignedTicket):
                        data = ticket
                    else:
                        data = ticket, cip
                    ticket_data = TICKET.validateTkt(data)
                    return True
                except Exception, e:
                    return None

                    #ticket_data = validateTicket(app.config['SECRET_KEY'], ticket,
                    #    timeout=app.config['TIME_OUT'], now=now, mod_auth_tkt=True)

                    #if ticket_data is not None:
                    #    return True

        return False
    except Exception, e:
        return False


def rpc_refresh_tkt(ticket=None):
    """ *validate_tkt* method
    """
    try:
        if ticket:
            ticket = binascii.a2b_base64(ticket)
            if ticket is None:
                return False

            cip = str(request.remote_addr)
            if isinstance(TICKET, SignedTicket):
                data = ticket
            else:
                data = ticket, cip
            ticket_data = TICKET.validateTkt(data)

            validuntil = int(time.time()) + TIMEOUT
            ticket = TICKET.createTkt(ticket_data[0], ticket_data[1], ticket_data[2], cip=cip, validuntil=validuntil)
            ticket_b64 = base64.b64encode(ticket)
            return ticket_b64

        return False
    except Exception, e:
        return False

############################################################################
# register xmlrpc callback    
handler.register(rpc_validate_tkt, "validate_tkt")
handler.register(rpc_login, "rpc_login")
handler.register(rpc_refresh_tkt, "refresh_tkt")
############################################################################

if __name__ == "__main__":
    app.run(port=6623, host='0.0.0.0', debug=True)
    #pass
