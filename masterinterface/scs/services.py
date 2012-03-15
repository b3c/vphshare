from pysimplesoap.client import SoapClient

def invokeSoapService( wsdl_url, service, port, method, requestParameters, requestType, responseType):
    """
        Invoke a soap method for a wsdl with only one service.

        Parameters:

            wsdl_url (string): the wsdl url

            service (string): the service this request is referred to

            port (string): the port this request is referred to

            method (string): the method name to be invoked

            requestParameters (dict): a dict with the request parameters

            requestType (django.db.models.Model): the request object type

            responseType (django.db.models.Model): the response object type

    """

    # create client
    client = SoapClient(wsdl=wsdl_url,trace=True)

    # create request string
    ## NOTE now it work good, but it need to test for a more complex request (es: complextype of complextype, sequence or array)
    request=""
    for name, Type in requestParameters.iteritems():

        request+=str(name)+"='"+str(Type)+"', "

    request=request[:-2]


    # invoke service
    try:

        call= 'client.'+method+'('+request+')'
        response=eval(str(call),globals(),locals())

    except Exception, e:
        response= "there was an error: %s" %str(e)

    # if response is a list the type in wsdl is arrayofType
    return response
    ##To Continue,if Mokup view need to render complex response, have to change it.
    """
    result={}
    # marshall response
    if type(response) == 'Text':
        result=response
    else:
        for name, Type in responseType:
            # arg is a tuple (name, type)

            if Type == 'ComplexType':
                complexType = client.factory.create( name )
                for key, value in complexType:
                    result[key] =  response[key]

            result[name] = response[name]
    return result

    """



