__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'


def get_file_data(f):
    buff = ""
    for chunk in f.chunks():
        buff += chunk
    return str(buff)
