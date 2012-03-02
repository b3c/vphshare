from django import template

# get a register Library instance
register = template.Library()

def breadcrumbs(path):
    base = '/'
    crumbs = []
    for crumb in str(path).split('/'):
        if not crumb:
            # skip empty
            continue
        current = "%s%s/" % (base,crumb)
        crumbs.append( dict( name=crumb, url= current ) )
        base = current
    return crumbs


# register filters
register.filter('breadcrumbs', breadcrumbs)