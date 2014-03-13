__author__ = 'Ernesto Coto'
import urllib2
import requests
import json
import time

USER = ''
PASSWD = ''
API_URL = 'http://127.0.0.1:8000/wfmng/'

def getAuthTicket(username, password):
    resp = urllib2.urlopen('http://devauth.biomedtown.org/user_login?domain=VPHSHARE&username=%s&password=%s' % (username, password))
    ticket = resp.read()
    if resp.code != 200:
        return None
    return ticket

# SAMPLE POST
# curl -X POST -H "MI-TICKET:<ticket_here>" "http://127.0.0.1:8000/wfmng/submit/" -F "global_id=b32e64f7-5897-4c9e-b8d5-cc7365edece2"

# SAMPLE GET
# curl -X GET -H "MI-TICKET:<ticket_here>" "http://127.0.0.1:8000/wfmng/<run_id_in_wm_database>"

# SAMPLE DELETE
# curl -X DELETE -H "MI-TICKET:<ticket_here>" "http://127.0.0.1:8000/wfmng/<run_id_in_wm_database>"

ticket = getAuthTicket(USER, PASSWD)
exit_output = ""
try:
    headers = { 'MI-TICKET': ticket }
    data = {}
    data['global_id']  = {'b32e64f7-5897-4c9e-b8d5-cc7365edece2'}
    response = requests.post( API_URL +'submit/', 
                         data = data, 
                         headers=headers,
                         verify=False)
    # print response.text
    exit_output = 'code: %d, response: %s' % (response.status_code, response.text)
    if response.status_code == 200:
        wfrun_id = response.text.replace('"','')
        if wfrun_id: 
            workflow_not_finished = True
            while workflow_not_finished:
                response = requests.get( API_URL + wfrun_id, 
                                     headers=headers,
                                     verify=False)
                exit_output = 'code: %d, response: %s' % (response.status_code, response.text)
                # print response.text
                if response.status_code == 200:
                    workflow_not_finished = ('Operating' in  response.text)
                    time.sleep(5)
                else:
                    workflow_not_finished = False
                    print 'WARNING: ' + exit_output
            if response.status_code == 200:
                response = requests.delete(API_URL + wfrun_id, 
                                            headers=headers,
                                            verify=False)
                exit_output = 'code: %d, response: %s' % (response.status_code, response.text)
                # print response.text
                if response.status_code == 200:
                    print 'OK: ' + exit_output
                    # TODO: Check if output files exists in LOBCDER. If they don't something went wrong during execution.
                else:
                    print 'WARNING: ' + exit_output
    else:
        print 'WARNING: ' + exit_output
except Exception as e:
    print 'CRITICAL: ' + exit_output

