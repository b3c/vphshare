import os
from pysimplesoap.simplexml import *

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

    def isSimpleType(self,Type):

        """
            check if type is a simple type
            # add new simple type to better performance
        """
        checkType=type(Type)
        if checkType is OrderedDict:
            return False
        if checkType is type:
           if Type in TYPE_MAP:
               return True
        if isinstance(Type,Alias):
            if Type.py_type in TYPE_MAP:
                return True

        return False

    def resolveType(self,Type):

        checkType=type(Type)

        if checkType is OrderedDict:
            return type([])
        if checkType is type:
            return Type
        if isinstance(Type,Alias):
            return Type.py_type

    def appendType(self,name,Type):

        """
            Add new type

        """
        if name in self.types:
            return
        if self.isSimpleType(Type):
            self.types[name]=self.resolveType(Type)
        else:
            self.types[name]=[]
            if type(Type)==list:
                Type=Type[0]
            for fieldName, fieldNameType in Type.iteritems():
                if fieldNameType is None:
                    continue

                self.types[name].append(self.process(fieldName,fieldNameType))


    def process(self,name,type):

        """
            Process complex type
        """

        if self.isSimpleType(type):

            return [name,self.resolveType(type)]

        else:

            self.appendType(name,type)
            return [name,self.resolveType(type)]

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

    FIELD_MAP = {str:['Char','max_length=CharField_max_length'],
                 unicode:['Char','max_length=CharField_max_length'],
                 bool:['Boolean',''],
                 int:['Integer',''],
                 long:['BigInteger',''],
                 float:['Float',''],
                 Decimal:['Decimal','max_digits=DecimalField_max_length, decimal_places=DecimalField_max_places'],
                 datetime.datetime:['DateTime','auto_now=True, auto_now_add=True'],
                 datetime.date:['Date','auto_now=False, auto_now_add=False'],
                }

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

        if type(fieldType) is OrderedDict:
            return False
        if fieldType in TYPE_MAP:
            return True
        return False

    def resolveType(self,Type):

        checkType=type(Type)

        if checkType is OrderedDict:
            # the Orderdict is a sequence but it have to test
            return  str(type([])).split('\'')[1], ""

        if checkType is type:

            return self.FIELD_MAP[Type][0],self.FIELD_MAP[Type][1]

        #Default Field
        return 'Char'
    #max_length=CharField_max_length
    def addType(self, TypeName, ElementsName ):
        """
        """
        self.modelsResult+=self.modelclass.format(MethodNameRequestType=TypeName)

        for element,Type in ElementsName:
            if self.isStadardFiled(Type):
                ElementType, Options=self.resolveType(Type)
                self.modelsResult+=self.element.format(ElementName=element, ElementType=ElementType, Options=Options)
            else:
                self.modelsResult+=self.complexElement.format(ElementName=element, ElementType=element)

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
        self.imports, self.importModelType, self.form_method, self.modelClass, self.model, self.SimpleType=self.mockupFormsFile.read().split(SPLIT_TAG)

    def addForm(self,methodName, modelTypes):


        modelclass=self.modelClass
        simplefield=""

        for methodNameRequestTypeName,methodNameRequestType in modelTypes:
            if methodNameRequestType == 'ComplexType':
                self.imports+=self.importModelType.format(MethodNameRequestType=methodNameRequestTypeName)
                modelclass+=self.model.format(MethodNameRequestType=methodNameRequestTypeName)
            else:
                simplefield+=self.SimpleType.format(MethodNameRequestType=methodNameRequestTypeName)

        if modelclass == self.modelClass:
            self.formsResult+=  self.form_method.format(MethodName=methodName,superClass="Form")
            self.formsResult+=simplefield
        else:
            self.formsResult+=  self.form_method.format(MethodName=methodName,superClass="ModelForm")
            self.formsResult+=simplefield+modelclass

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

    def addView(self,ServiceName, MethodName,RequestType,ResponseType,PortName,wsdl_url):
        self.imports+=self.imports_forms_modules.format(MethodName=MethodName)

        for name , Type in RequestType:
            RequestType=name

        for name , Type in ResponseType:
            ResponseType=name



        self.viewResult+=self.viewMethodClass.format(MethodName=MethodName,RequestType=RequestType,ResponseType=ResponseType,ServiceName=ServiceName,PortName=PortName,WsdlURL=wsdl_url)

    def getViewResult(self):
        return self.imports+self.viewResult

class baseHtml_template:
    """"""

    path=MOCKUP_ROOT+"/templates/mockup/base.html"

    mockupBaseFile=None

    baseHtml=""

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