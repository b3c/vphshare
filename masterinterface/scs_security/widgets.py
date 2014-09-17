# coding=utf-8
__author__ = 'Alfredo Saglimbeni'
from django import forms
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
USER_ATTR = (
    ('uData0', 'Username'),
    ('uData1', 'Full name'),
    ('uData2', 'E-mail'),
    ('uData3', 'Language'),
    ('uData4', 'Country'),
    ('uData5', 'Postal Code'),
)

FUNCTION = (
    ('%s', 'Equals to'),
    ('*%s*', 'Contains'),
    ('*%s', 'Starts with'),
    ('%s*', 'Ends with'),
)

class AdditionalUserAttribute(forms.Widget):
    """
    An additional widget to put in the form multiple input dinamicaly
    """

    def __init__(self, *args, **kwargs):
        """A widget that displays JSON Key Value Pairs
        as a list of text input box pairs

        kwargs:
        attribute_attrs -- html attributes applied to the 1st input box pairs
        conddition_attrs -- html attributes applied to the 2nd input box pairs
        value_attrs -- html attributes applied to the 3nd input box pairs

        """
        self.name_attrs = {}
        self.conddition_attrs = {}
        self.value_attrs = {}

        if "name_attrs" in kwargs:
            self.name_attrs = kwargs.pop("name_attrs")
        if "conddition_attrs" in kwargs:
            self.conddition_attrs = kwargs.pop("conddition_attrs")
        if "value_attrs" in kwargs:
            self.value_attrs = kwargs.pop("value_attrs")

        forms.Widget.__init__(self, *args, **kwargs)

    def render(self, fieldname, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """

        if value is None: value = ('','','')

        option = '<option value="%s" %s >%s</option>'
        user_attribute_name = ""
        for k,v in USER_ATTR:
            if k == value[0]:
                user_attribute_name += option % (k, 'selected', v)
            else:
                user_attribute_name += option % (k, '', v)

        user_attribute_condition = ""
        for k,v in FUNCTION:
            if k == value[1]:
                user_attribute_condition += option % (k, 'selected', v)
            else:
                user_attribute_condition += option % (k, '', v)
        ctx = {'name':user_attribute_name,
               'condition':user_attribute_condition,
               'value': value[2],
               'fieldname':fieldname,
               'name_attrs': flatatt(self.name_attrs),
               'conddition_attrs': flatatt(self.conddition_attrs),
               'value_attrs': flatatt(self.value_attrs)
        }

        ret = """
        <div class="row-fluid">
            <select class="user-attribute-name span2" name="user_attribute_name[%(fieldname)s]" %(name_attrs)s>%(name)s</select>
            <select class="user-attribute-condition span2" name="user_attribute_condition[%(fieldname)s]" %(conddition_attrs)s>%(condition)s</select>
            <input class="user-attribute-value span3" type="text" name="user_attribute_value[%(fieldname)s]" value="%(value)s" %(value_attrs)s>
            <input name="remove" class="btn btn-danger span2" value="remove" type="button">
        </div>
        """ % ctx

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
        if data.has_key('user_attribute_name[%s]' % name) and data.has_key('user_attribute_condition[%s]' % name) and data.has_key('user_attribute_value[%s]' % name):
            try:
                names      = data.getlist("user_attribute_name[%s]" % name)
                conditions = data.getlist("user_attribute_condition[%s]" % name)
                values     = data.getlist("user_attribute_value[%s]" % name)
            except Exception,e:
                # if getlist doesn't work the given data is a list and not a querydict
                names      = data['user_attribute_name[%s]'% name]
                conditions = data['user_attribute_condition[%s]'% name]
                values     = data['user_attribute_value[%s]'% name]
            for name, condition, value in zip(names, conditions, values):
                if len(name) > 0:
                    twotuple += [(name, condition, value)]
        return twotuple


class AdditionalPostField(forms.Widget):
    """
    An additional widget to put in the form multiple input dinamicaly
    """

    def __init__(self, *args, **kwargs):
        """A widget that displays JSON Key Value Pairs
        as a list of text input box pairs

        kwargs:
        attribute_attrs -- html attributes applied to the 1st input box pairs
        conddition_attrs -- html attributes applied to the 2nd input box pairs
        value_attrs -- html attributes applied to the 3nd input box pairs

        """
        self.name_attrs = {}
        self.conddition_attrs = {}
        self.value_attrs = {}

        if "name_attrs" in kwargs:
            self.name_attrs = kwargs.pop("name_attrs")
        if "conddition_attrs" in kwargs:
            self.conddition_attrs = kwargs.pop("conddition_attrs")
        if "value_attrs" in kwargs:
            self.value_attrs = kwargs.pop("value_attrs")

        forms.Widget.__init__(self, *args, **kwargs)

    def render(self, fieldname, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """

        if value is None: value = ('','','')

        option = '<option value="%s" %s >%s</option>'

        post_filed_condition = ""
        for k,v in FUNCTION:
            if k == value[1]:
                post_filed_condition += option % (k, 'selected', v)
            else:
                post_filed_condition += option % (k, '', v)
        ctx = {'name':value[0],
               'condition':post_filed_condition,
               'value': value[2],
               'fieldname':fieldname,
               'name_attrs': flatatt(self.name_attrs),
               'conddition_attrs': flatatt(self.conddition_attrs),
               'value_attrs': flatatt(self.value_attrs)
        }

        ret = """
        <div class="row-fluid">
            <input class="post-field-name span3" type="text" name="post_field_name[%(fieldname)s]" value="%(name)s" %(value_attrs)s>
            <select class="post-field-condition span2" name="post_field_condition[%(fieldname)s]" %(conddition_attrs)s>%(condition)s</select>
            <input class="post-field-value span3" type="text" name="post_field_value[%(fieldname)s]" value="%(value)s" %(value_attrs)s>
            <input name="remove" class="btn btn-danger span2" value="remove" type="button">
        </div>
        """ % ctx

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
        if data.has_key('post_field_name[%s]' % name) and data.has_key('post_field_condition[%s]' % name) and data.has_key('post_field_value[%s]' % name):
            try:
                names      = data.getlist("post_field_name[%s]" % name)
                conditions = data.getlist("post_field_condition[%s]" % name)
                values     = data.getlist("post_field_value[%s]" % name)
            except Exception,e:
                # if getlist doesn't work the given data is a list and not a querydict
                names      = data['post_field_name[%s]' % name]
                conditions = data['post_field_condition[%s]' % name]
                values     = data['post_field_value[%s]' % name]
                pass
            for name, condition, value in zip(names, conditions, values):
                if len(condition) > 0:
                    twotuple += [(name, condition, value)]
        return twotuple
