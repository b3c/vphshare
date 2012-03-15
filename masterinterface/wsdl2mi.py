__author__ = 'asaglimbeni'

#from suds import client
import sys, shutil
from  wsdl2mi_utils import *
from pysimplesoap.client import SoapClient


from django.core.management import execute_manager
import settings as masterInterfaceSettings

base_path=os.path.abspath(os.path.dirname(__file__))

def installService(service):
    """

    Install Service script.
    It loads wsdl's services , methods and complextype , build directory and files structs.

    """


    ########
    ## Start Process Wsdl
    ########

    #Global service Name
    serviceName=service['serviceName']

    #List of method
    methods=[]

    #Istance of Types , process the complessType.
    types=Types(None)

    #List of ports name
    ports=[]

    #Load wsdl's services, method and complexType

    for portName, port in service['ports'].iteritems():

        ports.append(portName)

        for methodName, method in port['operations'].iteritems():

            # Initialize Method object
            m=Method(methodName)

            # Process Input types
            if method['input'] is not None:
                for inputName, input in method['input'].iteritems():
                    # TODO it's not clear if OrderType in pysymplesoap library is a sequence input, so we have to provide form sequence input whit formset!
                    m.input.append([inputName,'ComplexType'])
                    types.appendType(inputName,input)

            # Process Output type
            if method['output'] is not None:
                for outputName, output in method['output'].iteritems():
                    # TODO the same of previous
                    m.output.append([outputName,'ComplexType'])
                    types.appendType(outputName,output)
            methods.append(m)



        ########
        ## End Process Wsdl
        ########
    
    
        ########
        ## Start Create dir struct and build file template.
        ########
    
    
        service_path=base_path+'/'+serviceName
    
        #Make directory
        if not os.path.exists(service_path):
            os.makedirs(service_path)
    
        if not os.path.exists(service_path+'/templates'):
            os.makedirs(service_path+'/templates')
    
        if not os.path.exists(service_path+"/templates/"+serviceName):
            os.makedirs(service_path+"/templates/"+serviceName)
    
        #Istance of templates
        models=models_template()
        forms=forms_template()
        views=views_template(serviceName)
        baseHtml=baseHtml_template()
        serviceHtml=serviceHtml_Template(serviceName)
        urls=Urls_Template(serviceName)
        indexHtml=indexHtml_Template(serviceName)
    
        # Create types in models file
    
        for TypeName in types.types:
    
            models.addType(TypeName,types.types[TypeName])

        #Create a base html file
        baseHtml.addBaseHtml(serviceName)
    
        #Process method and build file from template object

        for method in methods:
    
            methodName= method.name
    
            #Append view on viewsClass
            views.addView(serviceName,methodName,method.input,method.output,ports[0],wsdl_url)
    
            #Create a service html file.
            serviceHtml.addServiceHtml(methodName)
    
            urls.addUrl(methodName)
    
            #Create new form based on type input
            forms.addForm(methodName,method.input)
    
    
        ## Start create file
        modelsFile=file(service_path+'/models.py','w')
        modelsFile.write(models.getModelResult())
        modelsFile.close()
    
        formsFile=file(service_path+'/forms.py','w')
        formsFile.write(forms.getFormsResult())
        formsFile.close()
    
        viewsFile=file(service_path+'/views.py','w')
        viewsFile.write(views.getViewResult())
        viewsFile.close()
    
        baseHtmlfile=file(service_path+"/templates/"+serviceName+'/base.html','w')
        baseHtmlfile.write(baseHtml.getBaseHtmlResult())
        baseHtmlfile.close()
    
        indexHtmlFile=file(service_path+"/templates/"+serviceName+'/index.html','w')
        indexHtmlFile.write(indexHtml.getIndexHtml())
        indexHtmlFile.close()
    
        for serviceNameHtml in serviceHtml.name:
            serviceHtmlFile=file(service_path+"/templates/"+serviceName+"/"+serviceNameHtml+'.html','w')
            serviceHtmlFile.write(serviceHtml.getServiceHtml())
            serviceHtmlFile.close()
    
        initFile=file(service_path+'/__init__.py','w')
        initFile.close()
    
        urlsFile=file(service_path+'/urls.py','w')
        urlsFile.write(urls.getUrl())
        urlsFile.close()

        ## End create file
    
        ##Update setting and Urls on Master Inteface
    
        settingFile=file(base_path+'/settings.py','r')
        newsettingFile=settingFile.read().replace('\n\n    ##NEW_APP',',\n    \'masterinterface.'+serviceName+'\'\n\n    ##NEW_APP')
        settingFile.close()
        settingFile=file(base_path+'/settings.py','w')
        settingFile.write(newsettingFile)
        settingFile.close()
    
        ##Update setting and Urls on Master Inteface
    
        UrlFile=file(base_path+'/urls.py','r')
        newUrlFile=UrlFile.read().replace('\n\n    ##NEW_URL',',\n    url(r\'^'+serviceName+'/\', include(\'masterinterface.'+serviceName+'.urls\'))\n\n    ##NEW_URL')
        UrlFile.close()
        UrlFile=file(base_path+'/urls.py','w')
        UrlFile.write(newUrlFile)
        UrlFile.close()

        ########
        ## End Create dir struct and build file template.
        ########

        #Now we support only one entry Port
        break

if __name__ == '__main__':

    
    #    Main function. It starts install script with the wsdl url.
    
    print "Usage: %s <wsdl url>" % sys.argv[0]
    
    if len( sys.argv) < 2:
        print "\n please provide all inputs! "
        sys.exit(-1)

    # Some wsdl to try
    ## http://www.webservicex.net/WeatherForecast.asmx?WSDL

    ## http://graphical.weather.gov/xml/SOAP_server/ndfdXMLserver.php?wsdl

    ## "http://www.webservicex.net/sendsmsworld.asmx?WSDL"

    ## "http://peopleask.ooz.ie/soap.wsdl"

    ## "http://www.predic8.com:8080/shop/ShopService?wsdl"

    wsdl_url= sys.argv[1]


    client = SoapClient(wsdl=wsdl_url,trace=False)
    # print "Target Namespace", client.namespace



    #Check that service already exist , if not, go on.
    #This section have to be optimized to process more service more port
    #Now we process only one service (the main) and only one port for service.

    for serviceName, service in client.services.iteritems():

        settings=file(base_path+'/settings.py','r')
        settingFile=settings.read()
        settings.close()

        if settingFile.find(',\n    \'masterinterface.'+serviceName)>0:

            while True:
                print "\nService %s always exist, you can (D) Delete (R) Replace (A) Abort :\n" %serviceName
                response = sys.stdin.readline()
                if response[0] in ['D','d','R','r']:

                    if os.path.exists(base_path+'/'+serviceName):
                        shutil.rmtree(base_path+'/'+serviceName)

                    newsettingFile=settingFile.replace(',\n    \'masterinterface.'+serviceName+'\'','')

                    settingFile=file(base_path+'/settings.py','w')
                    settingFile.write(newsettingFile)
                    settingFile.close()

                    UrlFile=file(base_path+'/urls.py','r')
                    newUrlFile=UrlFile.read().replace(',\n    url(r\'^'+serviceName+'/\', include(\'masterinterface.'+serviceName+'.urls\'))','')
                    UrlFile.close()
                    UrlFile=file(base_path+'/urls.py','w')
                    UrlFile.write(newUrlFile)
                    UrlFile.close()
                    if response[0] in ['d','D']:
                        exit(0)
                    else:
                        break
                if response[0] == 'A':
                    exit(0)

        service['serviceName']=serviceName
        installService(service)
        break



    sys.argv.pop(1)
    sys.argv.append('syncdb')
    execute_manager(masterInterfaceSettings)
