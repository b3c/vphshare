from django import template
from django.db.models import Q
from datetime import datetime
from permissions.models import PrincipalRoleRelation
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import urlize as urlize_impl
from permissions.utils import get_roles
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
        res = str(string).split(sep)
        if '' in res:
            res.remove('')
        return res
    return []


def strTodate(date):
    try:
        try:
            return datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S.%f')
        except Exception, e:
            return datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')
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

@register.filter
def user_has_role(user, role):
    return role in get_roles(user)

@register.filter
def can_read(user, resource):
    return resource.can_read(user)

@register.filter
def can_edit(user, resource):
    return resource.can_edit(user)

@register.filter
def can_manage(user, resource):
    return resource.can_manage(user)

@register.filter
def is_public(resource):
    return resource.is_public()

@register.filter
def is_active(resource):
    return resource.is_active()

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

