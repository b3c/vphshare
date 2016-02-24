#!/bin/python

# python script to test csv to baclava example
from Taverna2WorkflowIO import Taverna2WorkflowIO
import sys


def get_file_data(f):
    buff = f.read().replace('\r', '')
    return buff


if __name__ == "__main__":
    # convert csv file
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as f:
            tio = Taverna2WorkflowIO()
            buff = get_file_data(f)
            tio.loadInputsFromCSVString(buff)
            with open(sys.argv[1] + ".xml", 'w') as fout:
                fout.write(tio.inputsToBaclava())
