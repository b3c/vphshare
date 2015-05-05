from masterinterface  import settings          #your project settings file
from django.core.management  import setup_environ     #environment setup function
setup_environ(settings)
from decryptPSdata import ps2share, get_lobcder_global_id, User, json
from migration_results import *
ticket = User.objects.get(username='asagli').userprofile.get_ticket()
count = 0
for res in MR.keys():
    for key, data in enumerate(MR[res]):
        count +=1
        #global_id = get_lobcder_global_id(data[5], ticket)
        #MR[res][key].append(global_id)
#outputresults= open('/home/pa/final_results.txt','w')
#outputresults.write(json.dumps(MR))
#ps2share()
print count
