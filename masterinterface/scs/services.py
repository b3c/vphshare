import suds

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
    client = suds.client.Client( wsdl_url )

    # create request object
    request = client.factory.create( requestType.__name__ )

    for key, value in request:
        # element is a tuple (key, value)
        request[ key ] = requestParameters[key]

    # invoke service
    response = client.service[port][method](request)

    # marshall response
    result= client.factory.create(responseType.__name__)
    #result = responseType()

    if type(response) is type([]):
        i=0
        for key, value in result:
            result[key]=response[i]
            i+=1
    else:
        result=response
    # HACK!!
    # for key,value in response:
    #    result[key] = value

   # result.sendSMSResult = str(response)


    return result



