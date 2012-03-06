import os
__author__ = 'asaglimbeni'

MOCKUP_ROOT = os.path.abspath(os.path.dirname(__file__))+'/mockup'
SPLIT_TAG="#-split-#"

class Method:

    """
        Load operation of wsdl with input and output arguments.
    """

    input=[]
    output=[]

    def __init__(self,name, input=None, output=None):
        """
            Init method class
        """
        if not input: input = []
        if not output: output = []
        self.input=input
        self.output=output
        self.name=name

    def __str__(self):
        """
            Print method object
        """

        s=""+self.name+"("
        s+=str(self.input)+") Return:["
        s+=str(self.output)
        s+="]"
        return s
    def appendInput(self,input):

        """
            add new input arg
        """

        self.input.append(input)

    def appendOutput(self,output):

        """
            add new output arg
        """

        self.output.append(output)

class Types:

    """
        Load types of wsdl

    """

    # types dictionary
    types={}


    def __init__(self,wsdl):
        """
            Init types object with wsdl (is a suds client istance)
        """
        self.wsdl=wsdl

    def isSimpleType(self,type):

        """
            check if type is a simple type
            # add new simple type to better performance
        """

        if type in ['string','int','integer','bool','float','dateTime','boolean','decimal','date','time']:
            return True
        return False


    def appendType(self,name,type):

        """
            Add new type

        """

        if self.isSimpleType(type):
            self.types[name]=type
        else:
            Complex=self.wsdl.factory.resolver.find(type)
            self.types[Complex.name]=[]
            for btype, ptype in Complex:
                self.types[Complex.name].append(self.process(btype.name,btype.type[0]))

    def process(self,name,type):

        """
            Process complex type
        """

        if self.isSimpleType(type):
            return [name,type]
            #self.Elem(name,type)
        else:
            Complex=self.wsdl.factory.resolver.find(type)
            self.appendType(Complex.name,Complex.name)
            return [name,type]
            #subc= {Complex.name: []}
            #for btype, ptype in Complex:
            #    subc[Complex.name].append(self.process(btype.name,btype.type[0]))
            #return subc

    def getType(self,typeName):

        """
            Return corresponding typeName form dictionary
        """

        return self.types[typeName]


    def __print__(self,typ):

        if isinstance(typ,type('')):
            return typ
        if isinstance(typ,type(unicode())):
            return typ
        if isinstance(typ,type([])):
            s="\n"
            for t in typ:
                s+=self.__print__(t)+"\n"
            s+=""
            return s
        if isinstance(typ,type({})):
            s=""
            for k,t in typ.iteritems():
                s+="("+k+"){\n  "
                s+=""+self.__print__(t)+"\n }\n"
            return s


    def __str__(self):

        """
            Print type object.
        """

        s="Type:\n"
        for k,t in self.types.iteritems():
            s+="("+k+"){\n  "
            s+=self.__print__(t)+"\n }\n"
        return s

####################
#### Start Template section
####################

class models_template:

    path=MOCKUP_ROOT+"/models.ppy"

    mockupModelsFile=None

    imports= None

    modelclass= None

    element= None

    complexElement= None

    modelsResult=""

    def __init__(self):
        """
        """
        self.mockupModelsFile=file(self.path,'r')

        self.imports, self.modelclass, self.element,self.complexElement=self.mockupModelsFile.read().split(SPLIT_TAG)
        self.modelsResult+=self.imports

    def __addElemtn(self, Element):

        if type(Element)==type([]):
            for element,Type in Element:
                self.modelsResult+=self.element.format(ElementName=element, ElementType=Type)


        if type(Element)==type({}):
            for element,Type in Element.iteritems:
                self.modelsResult+=self.element.format(ElementName=element, ElementType=Type)

    def isStadardFiled(self,fieldType):
        if fieldType in ['string','int','integer','bool','float','dateTime','boolean','decimal','date','time']:
            return True
        return False

    def addType(self, TypeName, ElementsName ):
        """
        """
        self.modelsResult+=self.modelclass.format(MethodNameRequestType=TypeName)

        for element,Type in ElementsName:
            if self.isStadardFiled(Type):
                self.modelsResult+=self.element.format(ElementName=element, ElementType='Char')
            else:
                self.modelsResult+=self.complexElement.format(ElementName=element, ElementType=Type)

    def getModelResult(self):

        return self.modelsResult

class forms_template:
    """"""

    path=MOCKUP_ROOT+"/forms.ppy"

    mockupFormsFile=None

    imports=None

    importModelType=None

    form_method=None

    model=None

    formsResult=""

    def __init__(self):
        """
        """
        self.mockupFormsFile=file(self.path,'r')
        self.imports, self.importModelType, self.form_method, self.model=self.mockupFormsFile.read().split(SPLIT_TAG)

    def addForm(self,methodName, modelTypes):
        self.formsResult+=  self.form_method.format(MethodName=methodName)

        for methodNameRequestType in modelTypes:
            self.imports+=self.importModelType.format(MethodNameRequestType=methodNameRequestType)
            self.formsResult+=self.model.format(MethodNameRequestType=methodNameRequestType)

    def getFormsResult(self):
        return self.imports+self.formsResult

class views_template:
    """"""

    path=MOCKUP_ROOT+"/views.ppy"

    mockupViewsFile=None

    imports=None

    imports_forms_modules=None

    viewMethodClass=None

    indexView=None

    viewResult=""

    def __init__(self,ServiceName):
        """
        """
        self.mockupViewsFile=file(self.path,'r')
        self.imports, self.imports_forms_modules, self.indexView, self.viewMethodClass=self.mockupViewsFile.read().split(SPLIT_TAG)

        self.viewResult+=self.indexView.format(ServiceName=ServiceName)

    def addView(self,ServiceName, MethodName,PortName,wsdl_url):
        self.imports+=self.imports_forms_modules.format(MethodName=MethodName)
        self.viewResult+=self.viewMethodClass.format(MethodName=MethodName,ServiceName=ServiceName,PortName=PortName,WsdlURL=wsdl_url)
        ###TODO
        ### COMPLETE CLASS: MORE SERVICE CASE.

    def getViewResult(self):
        return self.imports+self.viewResult

class baseHtml_template:
    """"""

    path=MOCKUP_ROOT+"/templates/mockup/base.html"

    mockupBaseFile=None

    baseHtml="""
<!-- Automatically generated by SCS Service Interface Generator -->

{{% extends 'base.html' %}}

{{% block title %}}
    Welcome to {ServiceName}
    <!-- the page tile goes here -->
{{% endblock %}}

{{% block extrahead %}}
    <!-- your styles, javascript and whatever you want to put into the page header go here -->
{{% endblock %}}

{{% block content %}} {{% endblock %}}
    """

    baseHtmlResult=""

    def __init__(self):
        """
        """
        self.mockupBaseFile=file(self.path,'r')
        self.baseHtml=self.mockupBaseFile.read().split(SPLIT_TAG)[0]


    def addBaseHtml(self,ServiceName):

        self.baseHtmlResult+= self.baseHtml.format(ServiceName=ServiceName)


    def getBaseHtmlResult(self):

        return self.baseHtmlResult

class serviceHtml_Template:
    """
    """

    path=MOCKUP_ROOT+"/templates/mockup/MethodName.html"

    mockupServiceFile=None

    name =[]

    serviceHtml=None



    def __init__(self,serviceName):
        """

        """
        self.mockupServiceFile=file(self.path,'r')
        self.serviceHtml=self.mockupServiceFile.read().split(SPLIT_TAG)[0]

        self.serviceHtml=self.serviceHtml.format(ServiceName=serviceName)


    def addServiceHtml(self,name):
        self.name.append(name)


    def getServiceHtml(self):
        return self.serviceHtml


class Urls_Template:
    """
    """

    path=MOCKUP_ROOT+"/urls.ppy"

    mockupUrlsFile=None

    imports=None

    importsView=None

    patterns=None

    urls=None

    indexUrl=None

    urlsResult=""

    patternsResult=""

    def __init__(self,serviceName):
        """

        """

        self.mockupUrlsFile=file(self.path,'r')
        self.imports, self.importsView, self.patterns, self.urls, self.indexUrl=self.mockupUrlsFile.read().split(SPLIT_TAG)

        self.patternsResult=self.patterns.format(ServiceName=serviceName)

    def addUrl(self,methodName):
        self.imports+=self.importsView.format(MethodName=methodName)
        self.patternsResult+=self.urls.format(MethodName=methodName)



    def getUrl(self):
        return self.imports+self.patternsResult+self.indexUrl


class indexHtml_Template:
    """
    """

    path=MOCKUP_ROOT+"/templates/mockup/index.html"

    mockupIndexFile=None

    indexHtml=None

    indexHtmlResult=""

    def __init__(self,serviceName):
        """

        """

        self.mockupIndexFile=file(self.path,'r')
        self.indexHtml=self.mockupIndexFile.read().split(SPLIT_TAG)[0]

        self.indexHtmlResult=self.indexHtml.format(ServiceName=serviceName)



    def getIndexHtml(self):
        return self.indexHtmlResult





####################
#### END Template section
#####################