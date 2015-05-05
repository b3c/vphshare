__author__ = 'm.balasso@scsitaly.com'

import os
from lxml import etree


def append_children(parent_node, dataresource):
    if dataresource.children:
        child_node = dataresource.xml.find(".//Children")
        child_node.attrib['NumberOfItems'] = str(len(dataresource.children))
        for child in dataresource.children:
            append_children(child_node, child)

    if dataresource.xml.tag == 'Root':
        dataresource.xml.tag = "Node"
        dataresource.xml.attrib['Type'] = "mafVMEGroup"

    parent_node.append(dataresource.xml)


def create_msf_from_tree(root, output_file):

    sample_msf_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sample.msf")

    msf = etree.fromstring(open(sample_msf_path, "r").read())

    msf_children_node = msf.find(".//Root//Children")

    append_children(msf_children_node, root)

    # fix ids
    node_id = 1

    for node in msf.iter('Node'):
        node.attrib['Id'] = str(node_id)
        node_id += 1

    msf.find(".//Root").attrib['MaxNodeId'] = str(node_id)

    fout = open(output_file, 'w')
    fout.write(etree.tostring(msf))
    fout.close()


