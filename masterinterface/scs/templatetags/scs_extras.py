from django import template
from django.db.models import Q
from datetime import datetime
from permissions.models import PrincipalRoleRelation
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import urlize as urlize_impl
# get a register Library instance
register = template.Library()


def basepath(path):
    base = str(path).split('/')[1]
    return base


def breadcrumbs(path):
    base = '/'
    crumbs = []
    for crumb in str(path).split('/'):
        if not crumb:
            # skip empty
            continue
        current = "%s%s/" % (base, crumb)
        crumbs.append(dict(name=crumb, url=current))
        base = current
    return crumbs


def split(string, sep=" "):
    if string is not None:
        return str(string).split(sep)
    return []


def strTodate(date):
    try:
        return datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S.%f')
    except Exception, e:
        return ''

@register.filter
def strCut(string, lenght):
    try:
        if len(string) > int(lenght):
            return string[:int(lenght)] + '....'
        return string
    except Exception, e:
        return ''


@register.filter
def keyvalue(dict, key):
    if key in dict:
        return dict[key]
    return '0'


def can_read(user, resource):
    # TODO check permissions rather than roles!
    # if resource.__class__.__name__ == "Resource":
    #     return has_permission(resource, user, 'can_read_resource')
    # else:
    #     parent = resource.resource_ptr
    #     return has_permission(parent, user, 'can_read_resource')

    role_relations = PrincipalRoleRelation.objects.filter(
        Q(user=user) | Q(group__in=user.groups.all()),
        content_id=resource.id
    )

    if role_relations.count() > 0:
        return True

    return False

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def urlizetrunctarget(value, limit, autoescape=None):
    """
    Converts URLs into clickable links, truncating URLs to the given character
    limit, and adding 'rel=nofollow' attribute to discourage spamming.

    Argument: Length to truncate URLs to.
    """
    return mark_safe(urlize_impl(value, trim_url_limit=int(limit), nofollow=True, autoescape=autoescape)).\
        replace('<a href=', '<a target="_blank" href=')


# register filters
register.filter('breadcrumbs', breadcrumbs)
register.filter('basepath', basepath)
register.filter('split', split)
register.filter('strTodate', strTodate)
register.filter('can_read',can_read)
