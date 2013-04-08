__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

import ConfigParser
import StringIO


def create_configuration_file(configurations={}):
    """
        create a properties file with the given properties
    """

    sample_configuration_file = """listening_port={listening_port}
outgoing_address={outgoing_address}
outgoing_port={outgoing_port}
granted_roles=^((?!/(admin/?)).)*$:{granted_roles};.*/admin/?:admin"""

    return sample_configuration_file.format(**configurations)


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

