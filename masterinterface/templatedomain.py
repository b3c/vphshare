from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from masterinterface.scs_groups.models import Institution

def domainx(request):
   '''
   A context processor to add the "GROUP SUBDOMAIN" to the current Context
   '''
   try:
	current_url = request.build_absolute_uri
	a = current_url()
	b = a.replace("http://", "")
	c = b.split('.mi.')
	c = c[0]

	if c == b: # if we are in the PORTAL
	    return {
		'current_url': current_url,
		'current_subdomain_url': 'PORTAL',
		'group_subdomain' : '', 
		'group_subdomain_name' : 'VPH-SHARE', 
		'base_group' : 'scs/base.html',
		'group_images' : '/static/img/'
	    }	
	else:
		groupx = Institution.objects.get(subdomain=c) #Add except Site.DoesNotExist ...
		if groupx != None :
	    	   return {		
			'current_url': current_url,
			'current_subdomain_url': c,
			'group_subdomain' : groupx.subdomain, 
			'group_background' : groupx.background,
			'group_header_background' : groupx.header_background,
			'group_subdomain_name' : groupx.subdomain_name,
			'base_group' : 'scs/base_group.html',
			'group_images' : '/static/groups/' + groupx.subdomain + '/', # location: masterinterface/img/groups/+group_subdomain
	   	   }

   except Site.DoesNotExist:
        return {'current_url':''} 
