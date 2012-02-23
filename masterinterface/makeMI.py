__author__ = 'asaglimbeni'
from suds import client


class Method:

    input=[]
    output=[]

    def __init__(self,name, input=None, output=None):

        if not input: input = []
        if not output: output = []
        self.input=input
        self.output=output
        self.name=name

    def __str__(self):
        s=""+self.name+"("
        s+=str(self.input)+") Return:["
        s+=str(self.output)
        s+="]"
        return s
    def appendInput(self,input):
        self.input.append(input)

    def appendOutput(self,output):
        self.output.append(output)

class Types:
    types={}


    class Elem():

        def __init__(self , name=None , type=None):

            self.name=name
            self.type=type

        def __str__(self):

            s="("
            s+=str(self.name)+" , "
            s+=str(self.type)+")"

            return s

    def __init__(self,client):
        self.client=client

    def __isSimpleType(self,type):
        if type in ['string','int','bool']:
            return True
        return False


    def appendType(self,name,type):
        if self.__isSimpleType(type):
            self.types[name]=type
        else:
            Complex=self.client.factory.resolver.find(type)
            self.types[Complex.name]=[]
            for btype, ptype in Complex:
                self.types[Complex.name].append(self.process(btype.name,btype.type[0]))

    def process(self,name,type):

        if self.__isSimpleType(type):
            return self.Elem(name,type)
        else:
            Complex=self.client.factory.resolver.find(type)
            subc= {Complex['name']: []}
            for btype, ptype in Complex:
                    subc[Complex['name']].append(self.process(btype.name,btype.type[0]))
            return subc


    def __print__(self,typ):
        if isinstance(typ,type('')):
            return typ
        if isinstance(typ,self.Elem):
            return str(typ)
        if isinstance(typ,type([])):
            s="\n"
            for t in typ:
                s+=self.__print__(t)+"\n"
            s+=""
            return s
        if isinstance(typ,type({})):
            for k,t in self.types.iteritems():
                s+="("+k+"){\n  "
            s+=self.__print__(t)+"\n }"
            return s


    def __str__(self):
        s="Type:\n"
        for k,t in self.types.iteritems():
            s+="("+k+"){\n  "
            s+=self.__print__(t)+"\n }\n"
        return s


#####################
url= "http://www.webservicex.net/sendsmsworld.asmx?WSDL"
Client =client.Client(url)

methods=[]
types=Types(Client)

for service in Client.wsdl.services:
    print "====== service"
    for port in service.ports:
        for method in port.methods.values():

            m=Method(method.name)

            for part in method.soap.input.body.parts:
                m.input.append(part.element[0])
                types.appendType(part.element[0],part.element[0])

            for part in method.soap.output.body.parts:
                m.output.append(part.element[0])
                types.appendType(part.element[0],part.element[0])

            methods.append(m)

for method in methods:
    print method
print "---------------------------"
print types

