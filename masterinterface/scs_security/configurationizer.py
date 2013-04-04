__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'


__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from lxml import etree


def create_configuration_file(configurations={}):
    """
        create a properties file with the given properties
    """

    sample_configuration_file = """listening_port={port}

outgoing_address={outgoing_address}
outgoing_port={outgoing_port}

granted_roles=^((?!/(admin/?)).)*$:{role};.*/admin/?:admin"""

    return sample_configuration_file.format(configurations)


def extract_configurations(configuration_file=""):
    """
        extract properties dictionary from given properties file
    """

    return {}

