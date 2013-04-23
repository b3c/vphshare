__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

import ConfigParser
import StringIO


def create_configuration_file(configurations={}):
    """
        create a properties file with the given properties
    """

    lines = []

    if 'listening_port' in configurations and configurations['listening_port']:
        lines.append("listening_port=%s" % configurations['listening_port'])
    if 'outgoing_address' in configurations and configurations['outgoing_address']:
        lines.append("outgoing_address=%s" % configurations['outgoing_address'])
    if 'outgoing_port' in configurations and configurations['outgoing_port']:
        lines.append("outgoing_port=%s" % configurations['outgoing_port'])
    if 'granted_roles' in configurations and configurations['granted_roles']:
        lines.append("granted_role=^((?!/(admin/?)).)*$:%s;.*/admin/?:admin" % configurations['granted_roles'])

    return "\n".join(lines)


def extract_configurations(configuration_file=""):
    """
        extract properties dictionary from given properties file
    """

    props = {}

    # add a fake section header and pass the buffer to the configparser
    buff = StringIO.StringIO(buf='[configurations]\n%s' % configuration_file)
    parser = ConfigParser.ConfigParser()
    parser.readfp(buff)
    props.update(parser.items('configurations'))

    # change granted_roles regex to be human readable
    # from
    # ^((?!/(admin/?)).)*$:{role};.*/admin/?:admin
    # to
    # {role}

    if 'granted_roles' in props:
        try:
            a = props['granted_roles']
            props['granted_roles'] = a[a.find(')*$:') + 4:a.find(';.*/admin/')]
        except:
            pass

    return props

