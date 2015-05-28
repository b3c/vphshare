<VirtualHost *:<port-443-or-80> > 
    DocumentRoot <master-interface-folder>
    ServerAdmin alert@scsitaly.com
    ServerName <master-interface-main-domain>
    #alias to redirect all the subdomain (institutional portal) 
    ServerAlias *.<master-interface-domain>
    HostnameLookups Off
    UseCanonicalName Off
    ServerSignature On
    #If you don't have the SSL keys leave commented
    #SSLEngine on
    #SSLProtocol all -SSLv2
    #SSLCertificateFile <your-certificate>
    #SSLCertificateChainFile <your-chain>
    #SSLCertificateKeyFile    <your-key>
    #SetEnvIf User-Agent ".*MSIE.*" nokeepalive ssl-unclean-shutdown
    #

    Alias /static/ <master-interface-folder>/static/

    <Directory "<master-interface-folder>/static/">
         Order deny,allow
         Allow from all
    </Directory>
    <Directory "<master-interface-folder>">
        AllowOverride None
        Order allow,deny
        Allow from all
    </Directory>

    WSGIPassAuthorization On
    WSGIScriptAlias /api/auth <authentication-services-folder>/authentication/authentication.wsgi
    WSGIScriptAlias / <master-interface-folder>/master.wsgi

    #Install libapache2-mod-auth-tkt  packet from apt-get
    Include /etc/apache2/mods-available/auth_tkt.conf
    <Location /api/auth/login>
        AuthType None
        require valid-user
        TKTAuthGuestLogin on
        TKTAuthBackArgName came_from
        TKTAuthDomain <master-interface-domain>
	    TKTAuthTimeout 0
	    TKTAuthSecret "secret"
    </Location>
</VirtualHost>
