__author__ = 'Alfredo Saglimbeni'
import simplejson
from django.forms import Widget
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt

class AdditionalLink(Widget):
    """A widget that displays JSON Key Value Pairs
    as a list of text input box pairs

    Usage (in forms.py) :
    examplejsonfield = forms.CharField(label  = "Example JSON Key Value Field", required = False,
                                       widget = JsonPairInputs(val_attrs={'size':35},
                                                               key_attrs={'class':'large'}))

    """

    def __init__(self, *args, **kwargs):
        """A widget that displays JSON Key Value Pairs
        as a list of text input box pairs

        kwargs:
        key_attrs -- html attributes applied to the 1st input box pairs
        val_attrs -- html attributes applied to the 2nd input box pairs

        """
        self.key_attrs = {}
        self.val_attrs = {}
        if "key_attrs" in kwargs:
            self.key_attrs = kwargs.pop("key_attrs")
        if "val_attrs" in kwargs:
            self.val_attrs = kwargs.pop("val_attrs")
        Widget.__init__(self, *args, **kwargs)

    def render(self, name, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """

        if value is None or value.strip() is '': value = ('','')


        ret = ''
        ctx = {'key':value[0],
               'value':value[1],
               'fieldname':name,
               'key_attrs': flatatt(self.key_attrs),
               'val_attrs': flatatt(self.val_attrs) }
        ret += '<div class="row-fluid"><div class="span4"><input class="link-description" type="text" name="description_key[%(fieldname)s]" value="%(key)s" %(key_attrs)s></div><div class="span4"> <input class="link-value" type="text" name="link_value[%(fieldname)s]" value="%(value)s" %(val_attrs)s></div><div class="btn btn-danger span3">Remove</div></div>' % ctx
        return mark_safe(ret)

    def value_from_datadict(self, data, files, name):
        """
        Returns the simplejson representation of the key-value pairs
        sent in the POST parameters

        args:
        data  (dict)  -- request.POST or request.GET parameters
        files (list)  -- request.FILES
        name  (str)   -- the name of the field associated with this widget

        """
        twotuple = []
        if data.has_key('description_key[%s]' % name) and data.has_key('link_value[%s]' % name):
            keys     = data.getlist("description_key[%s]" % name)
            values   = data.getlist("link_value[%s]" % name)
            for key, value in zip(keys, values):
                if len(key) > 0:
                    twotuple += [(key,value)]
        return twotuple

class AdditionalFile(Widget):
    """A widget that displays JSON Key Value Pairs
    as a list of text input box pairs

    Usage (in forms.py) :
    examplejsonfield = forms.CharField(label  = "Example JSON Key Value Field", required = False,
                                       widget = JsonPairInputs(val_attrs={'size':35},
                                                               key_attrs={'class':'large'}))

    """

    def __init__(self, *args, **kwargs):
        """A widget that displays JSON Key Value Pairs
        as a list of text input box pairs

        kwargs:
        key_attrs -- html attributes applied to the 1st input box pairs
        val_attrs -- html attributes applied to the 2nd input box pairs

        """
        self.key_attrs = {}
        self.val_attrs = {}
        if "key_attrs" in kwargs:
            self.key_attrs = kwargs.pop("key_attrs")
        if "val_attrs" in kwargs:
            self.val_attrs = kwargs.pop("val_attrs")
        Widget.__init__(self, *args, **kwargs)

    def render(self, name, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """

        if value is None or value.strip() is '': value = ('','')


        ret = ''
        ctx = {'key':value[0],
               'value':value[1],
               'fieldname':name,
               'key_attrs': flatatt(self.key_attrs),
               'val_attrs': flatatt(self.val_attrs) }
        ret += '<div class="row-fluid"><div class="span4"><input class="file-description" type="text" name="filedescription_key[%(fieldname)s]" value="%(key)s" %(key_attrs)s></div><div class="span4"> <input class="file-value" type="file" name="file_value[%(fieldname)s]" value="%(value)s" %(val_attrs)s></div><div class="btn btn-danger span3">Remove</div></div>' % ctx
        return mark_safe(ret)

    def value_from_datadict(self, data, files, name):
        """
        Returns the simplejson representation of the key-value pairs
        sent in the POST parameters

        args:
        data  (dict)  -- request.POST or request.GET parameters
        files (list)  -- request.FILES
        name  (str)   -- the name of the field associated with this widget

        """
        twotuple = []
        if data.has_key('filedescription_key[%s]' % name) and files.has_key('file_value[%s]' % name):
            keys     = data.getlist("filedescription_key[%s]" % name)
            values   = files.getlist("file_value[%s]" % name)
            for key, value in zip(keys, values):
                if len(key) > 0:
                    twotuple += [(key,value)]
        return twotuple