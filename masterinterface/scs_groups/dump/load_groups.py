__author__ = 'Teo'

import json
import os
from django.contrib.auth.models import User, Group
from masterinterface.scs_groups.models import VPHShareSmartGroup, Institution, Study

# load json dumps
dump_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
scs_groups_dump = json.loads(open(os.path.join(dump_folder, 'scs_groups.json'), "r").read())
auth_dump = json.loads(open(os.path.join(dump_folder, 'auth.json'), "r").read())

institutions = [x for x in scs_groups_dump if x['model'] == 'scs_groups.institution']
studies = [x for x in scs_groups_dump if x['model'] == 'scs_groups.study']
smarts = [x for x in scs_groups_dump if x['model'] == 'scs_groups.vphsharesmartgroup']

groups = [x for x in auth_dump if x['model'] == 'auth.group']
users = [x for x in auth_dump if x['model'] == 'auth.user']

# join models with auth.group
for dumped in smarts:
    dumped['name'] = [x for x in groups if x['pk'] == dumped['pk']][0]['fields']['name']

for dumped in institutions:
    dumped['name'] = [x for x in groups if x['pk'] == dumped['pk']][0]['fields']['name']

for dumped in studies:
    dumped['name'] = [x for x in groups if x['pk'] == dumped['pk']][0]['fields']['name']

def load():
    for dumped in smarts:
        print dumped
        new, created = VPHShareSmartGroup.objects.get_or_create(id=dumped['pk'], name=dumped['name'], active=dumped['fields']['active'])
        for user_pk in dumped['fields']['managers']:
            new.managers.add(User.objects.get(pk=user_pk))
        new.save()

    for dumped in institutions:
        print dumped
        new, created = Institution.objects.get_or_create(id=dumped['pk'], name=dumped['name'])
        for user_pk in dumped['fields']['managers']:
            try:
                new.managers.add(User.objects.get(pk=user_pk))
            except Exception, e:
                pass
        for key in dir(new):
            if key in dumped['fields']:
                setattr(new, key, dumped['fields'][key])
        new.save()

    for dumped in studies:
        print dumped
        new, created = Study.objects.get_or_create(id=dumped['pk'], name=dumped['name'], institution=Institution.objects.get(pk=dumped['fields']['institution']))
        new.parent = Institution.objects.get(pk=dumped['fields']['institution'])
        for user_pk in dumped['fields']['principals']:
            try:
                new.managers.add(User.objects.get(pk=user_pk))
            except Exception, e:
                pass
        for key in dir(new):
            if key in dumped['fields'] and key != 'institution':
                setattr(new, key, dumped['fields'][key])
        new.save()

    # restore users groups subscriptions

    for user in users:
        try:
            user_db = User.objects.get(pk=user['pk'])
        except Exception, e:
            continue

        for group_pk in user['fields']['groups']:
            user_db.groups.add(Group.objects.get(pk=group_pk))


