__author__ = 'Ernesto Coto'

import xmltodict
import base64
import types

class Taverna2WorkflowIO(object):
    """
    Class for allowing the management of Taverna 2.x workflows inputs and outputs.
    Note that this class only supports input/output ports of depth 0 and depth 1.

    Fields:

            inputsDic (dictionary): data structure holding the mapping of input ports to input port values.
            outputsDic (dictionary): data structure holding the mapping of output ports to output port values.
    """

    inputsDic = {}
    outputsDic = {}

    def toString(self):
        """ Returns a simple string version of the contents of the class. """
        return "INPUTS = %s.\nOUTPUTS = %s" % (str(self.inputsDic), str(self.outputsDic))

    def getInputPorts(self):
        """ Returns a list with the input ports names. """
        return self.inputsDic.keys()

    def getOutputPorts(self):
        """ Returns a list with the output ports names. """
        return self.outputsDic.keys()

    def setInputPorts(self, ports_list):
        """ Sets the list of input ports names.

            Fields:

                ports_list (list): list of input ports names.
        """
        try:
            self.inputsDic = dict.fromkeys(ports_list)
        except Exception:
            self.inputsDic = {}
            pass

    def setOutputPorts(self, ports_list):
        """ Sets the list of input ports names.

            Fields:

                ports_list (list): list of output ports names.
        """
        try:
            self.outputsDic = dict.fromkeys(ports_list)
        except Exception:
            self.outputsDic = {}
            pass

    def setInputPortValues(self, port_str, values_list):
        """ Sets the input values for a specific port.
            Won't do anything if the port is not defined or values_list is not a list.

            Fields:

                port_str (string): name of port to modify.
                values_list (list): list of input values.
        """
        if port_str in self.inputsDic.keys() and type(values_list) is list:
            self.inputsDic[port_str] = values_list

    def setReferenceOutputPortValues(self, port_str, values_list):
        """ Sets the reference output values for a specific port.
            Note that these output values are for reference only. Real output values are only obtained by running the workflow.
            Won't do anything if the port is not defined or values_list is not a list.

            Fields:

                port_str (string): name of port to modify.
                values_list (list): list of output values.
        """
        if port_str in self.outputsDic.keys() and type(values_list) is list:
            self.outputsDic[port_str] = values_list

    def getInputPortValues(self, port_str):
        """ Returns the input values for a specific port.
            Returns None if the port is not defined.

            Fields:

                port_str (string): name of port to query
        """
        if port_str in self.inputsDic.keys():
            return self.inputsDic[port_str]
        return None;

    def getReferenceOutputPortValues(self, port_str):
        """ Returns the reference output values for a specific port.
            Note that these output values are for reference only. Real output values are only obtained by running the workflow.
            Returns None if the port is not defined.

            Fields:

                port_str (string): name of port to query
        """
        if port_str in self.outputsDic.keys():
            return self.outputsDic[port_str]
        return None;

    def loadInputsFromCSVString(self, csv_str):
        """ Loads the input ports and values from a CSV-style string.

            Fields:

                csv_str (string): a CSV-style string.
        """
        if csv_str == None or not type(csv_str) is str:
            return
        try:
            lines = csv_str.split('\n')
            inputPorts = lines[0].split(',')
            self.inputsDic = dict.fromkeys(inputPorts)
            for i in range(len(self.inputsDic)):
               self.inputsDic[ inputPorts[i] ] = []
            for numLine in range(1,len(lines)):
                if len(lines[numLine])>0:
                    vals = lines[numLine].split(',')
                    for i in range(len(inputPorts)):
                        if vals[i]!='':
                            self.inputsDic[ inputPorts[i] ].append(vals[i])
        except Exception as e:
            raise Exception('Error while acquiring inputs from CSV String: ' + e.message)


    def loadInputsFromCSVFile(self, filePath_str):
        """ Loads the input ports and values from a CSV file.

            Fields:

                filePath_str (string): full path of input CSV file.
        """
        content = ""
        try:
            with open(filePath_str, 'r') as content_file:
                content = content_file.read()
                self.loadInputsFromCSVString(content)
        except Exception as e:
            raise Exception('Error while acquiring inputs from CSV: ' + e.message)

    def loadInputsFromBaclavaString(self, baclava_xml_str):
        """ Loads the input ports and values from a baclava-xml-style string.

            Fields:

                baclava_xml_str (string): a baclava-xml-style string.
        """
        try:
            baclavaContent = xmltodict.parse(baclava_xml_str)
            singlePort = None  # special treatment for input definitions that specify only one input port          
            for dataThing in baclavaContent['b:dataThingMap']['b:dataThing']:
                if dataThing=='@key': # special treatment for input definitions that specify only one input port
                    singlePort = baclavaContent['b:dataThingMap']['b:dataThing']['@key']
                    myGridDataDocument = baclavaContent['b:dataThingMap']['b:dataThing']['b:myGridDataDocument']
                    continue
                elif dataThing<>'b:myGridDataDocument' :
                    myGridDataDocument = dataThing.get('b:myGridDataDocument', None)
                partialOrder = myGridDataDocument.get('b:partialOrder', None)
                # if partialOrder tag is not found, the input corresponds to a single value
                if partialOrder is None:
                    dataElement = myGridDataDocument.get('b:dataElement', None)
                    elementData = dataElement['b:dataElementData']
                    decodedString = base64.b64decode(elementData)
                    if singlePort!=None:
                        self.inputsDic[ singlePort ] = [ decodedString]
                        singlePort = None
                    else:
                        self.inputsDic[ dataThing['@key']   ] = [ decodedString]
                else:
                # if partialOrder tag is found, the input corresponds to a list of values
                    if u'@type' in partialOrder and partialOrder[u'@type'] == "list":
                        itemList = partialOrder.get('b:itemList', None).items()[0][1]
                        if not(type(itemList) is list):
                            itemList = [{'b:dataElementData':  itemList['b:dataElementData'], u'@index':  u'0'}]
                        for dataElement in itemList:
                            # take the input file string, decode it, insert the new folder name on it an modify the input definition XML
                            elementData = dataElement['b:dataElementData']
                            decodedString = base64.b64decode(elementData)
                            # print "decodedString", decodedString
                            # print "singlePort", singlePort
                            port = None
                            if singlePort!=None:
                                port = singlePort
                            else:
                                port = dataThing['@key']
                            if port in self.inputsDic.keys():
                                self.inputsDic[ port ].append(decodedString)
                            else:
                                self.inputsDic[ port ] = [ decodedString ]
                        if singlePort!=None:
                            singlePort = None
        except Exception as e:
            raise Exception('Error while acquiring inputs from Baclava string: ' + e.message)

    def loadInputsFromBaclavaFile(self, filePath_str):
        """ Loads the input ports and values from a baclava file.

            Fields:

                filePath_str (string): full path of input baclava file.
        """
        content = ""
        try:
            with open(filePath_str, 'r') as content_file:
                content = content_file.read()
                self.loadInputsFromBaclavaString(content)
        except Exception as e:
            raise Exception('Error while acquiring inputs from Baclava: ' + e.message)

    def loadFromT2FLOWString(self, t2flow_str):
        """ Loads the input ports and values from a T2FLOW-style string.
            The input/output values are taken from the sample values for each port as specified in the annotations stored in the T2FLOW.

            Fields:

                t2flow_str (string): a T2FLOW-style string.
        """
        try:

            t2flowDict = xmltodict.parse(t2flow_str)

            # inputs
            if type(t2flowDict['workflow']['dataflow']) is list:
                inputPorts = t2flowDict['workflow']['dataflow'][0]['inputPorts']
            else:
                inputPorts = t2flowDict['workflow']['dataflow']['inputPorts']
            inputPortsList = []
            if type(inputPorts['port']) is list:
                for port in inputPorts['port']:
                    inputPortsList.append(port['name'])
                self.setInputPorts(inputPortsList)
                try:
                    for port in inputPorts['port']:
                        inputPortAnnotation = port['annotations']
                        if inputPortAnnotation!=None:
                            if type(inputPortAnnotation['annotation_chain'] ) is list:
                                for annotation in inputPortAnnotation['annotation_chain']:
                                    if "ExampleValue" in str(annotation):
                                          listWithSample = annotation[ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']['text'].split(",")
                                          self.setInputPortValues(port['name'], listWithSample)
                            else:
                                inputAnnotationBean = inputPortAnnotation['annotation_chain'][ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']
                                if "ExampleValue" in str(inputAnnotationBean):
                                    listWithSample = inputAnnotationBean['text'].split(",")
                                    self.setInputPortValues(port['name'], listWithSample)
                except:
                    pass # something went wrong reading the sample input values, but the port were acquired so we can continue
            else:
                self.setInputPorts( [ inputPorts['port']['name'] ] )
                try:
                    inputPortAnnotation = inputPorts['port']['annotations']
                    if inputPortAnnotation!=None:
                        if type(inputPortAnnotation['annotation_chain'] ) is list:
                            for annotation in inputPortAnnotation['annotation_chain']:
                                if "ExampleValue" in str(annotation):
                                    listWithSample = annotation[ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']['text'].split(",")
                                    self.setInputPortValues(inputPorts['port']['name'], listWithSample)
                        else:
                            inputAnnotationBean = inputPortAnnotation['annotation_chain'][ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']
                            if "ExampleValue" in str(inputAnnotationBean):
                                listWithSample = inputAnnotationBean['text'].split(",")
                                self.setInputPortValues(inputPorts['port']['name'], listWithSample)
                except:
                    pass # something went wrong reading the sample input values, but the port were acquired so we can continue

            # outputs
            if type(t2flowDict['workflow']['dataflow']) is list:
                outputPorts = t2flowDict['workflow']['dataflow'][0]['outputPorts']
            else:
                outputPorts = t2flowDict['workflow']['dataflow']['outputPorts']
            outputPortsList = []
            if type(outputPorts['port']) is list:
                for port in outputPorts['port']:
                    outputPortsList.append(port['name'])
                self.setOutputPorts(outputPortsList)
                try:
                    for port in outputPorts['port']:
                        outputPortAnnotation = port['annotations']
                        if outputPortAnnotation!=None:
                            if type(outputPortAnnotation['annotation_chain'] ) is list:
                                for annotation in outputPortAnnotation['annotation_chain']:
                                    if "ExampleValue" in str(annotation):
                                          listWithSample = annotation[ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']['text'].split(",")
                                          self.setReferenceOutputPortValues(port['name'], listWithSample)
                            else:
                                outputAnnotationBean = outputPortAnnotation['annotation_chain'][ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']
                                if "ExampleValue" in str(outputAnnotationBean):
                                    listWithSample = outputAnnotationBean['text'].split(",")
                                    self.setReferenceOutputPortValues(port['name'], listWithSample)
                except:
                    pass # something went wrong reading the sample output values, but the ports were acquired so we can continue
            else:
                self.setOutputPorts( [ outputPorts['port']['name']] )
                try:
                    outputPortAnnotation = outputPorts['port']['annotations']
                    if outputPortAnnotation!=None:
                        if type(outputPortAnnotation['annotation_chain'] ) is list:
                            for annotation in outputPortAnnotation['annotation_chain']:
                                if "ExampleValue" in str(annotation):
                                    listWithSample = annotation[ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']['text'].split(",")
                                    self.setReferenceOutputPortValues(outputPorts['port']['name'], listWithSample)
                        else:
                            outputAnnotationBean = outputPortAnnotation['annotation_chain'][ 'net.sf.taverna.t2.annotation.AnnotationChainImpl']['annotationAssertions']['net.sf.taverna.t2.annotation.AnnotationAssertionImpl']['annotationBean']
                            if "ExampleValue" in str(outputAnnotationBean):
                                listWithSample = outputAnnotationBean['text'].split(",")
                                self.setReferenceOutputPortValues(outputPorts['port']['name'], listWithSample)
                except:
                    pass # something went wrong reading the sample output values, but the ports were acquired so we can continue

        except Exception as e:
            raise Exception('Error while acquiring inputs/outputs from T2flow string: ' + e.message)

    def loadFromT2FLOWFile(self, t2flowPath_str):
        """ Loads the input ports and values from a T2FLOW file.
            The input/output values are taken from the sample values for each port as specified in the annotations stored in the T2FLOW.

            Fields:

                t2flowPath_str (string): full path of input T2FLOW file.
        """
        content = ""
        try:
            with open(t2flowPath_str, 'r') as content_file:
                content = content_file.read()
                self.loadFromT2FLOWString(content)
        except Exception as e:
            raise Exception('Error while acquiring inputs/outputs from T2flow: ' + e.message)

    def inputsToBaclava(self):
        """ Returns an XML in baclava format corresponding to previously specified input ports and values. """

        if len(self.inputsDic)==0:
            return None;

        try:
            enclosingDicMap = {}
            enclosingDicMap['@xmlns:b']='http://org.embl.ebi.escience/baclava/0.1alpha'
            baclavaDic = { 'b:dataThingMap': enclosingDicMap}
            baseDoc = xmltodict.unparse(baclavaDic, pretty=True)
            fullDataThingStringList = ""
            for port in self.inputsDic.keys():
                if self.inputsDic[port]!=None:
                    mimeTypesDict = { 's:mimeTypes' : {'s:mimeType' : 'text/plain'}}
                    mimeTypesDict['@xmlns:s'] = 'http://org.embl.ebi.escience/xscufl/0.1alpha'
                    metadataDict = { 's:metadata' : mimeTypesDict}
                    metadataDict[ '@lsid'] =''
                    metadataDict[ '@syntactictype']="'text/plain'"
                    if len(self.inputsDic[port])==1:
                        dataElementDataDict = { 'b:dataElementData': base64.b64encode(self.inputsDic[port][0])}
                        dataElementDataDict [ '@lsid'] =''
                        metadataDict[ 'b:dataElement'] = dataElementDataDict
                    else:
                        relationEmptyDict = [{ '@parent': "0", '@child': "1" }]
                        for i in range(2,len(self.inputsDic[port])):
                            relationEmptyDict.append({  '@parent': str(i-1), '@child': str(i) })
                        relationDict = { 'b:relation' : relationEmptyDict }
                        relationListDict = { 'b:relationList': relationDict , '@lsid': "" , '@type': "list"}
                        dataElementDataDict = []
                        for i in range(len(self.inputsDic[port])):
                            dataElementDataDict.append( { 'b:dataElementData': base64.b64encode(self.inputsDic[port][i]), '@lsid': "", '@index': str(i)} )
                        dataElementDict = { 'b:dataElement':  dataElementDataDict}
                        relationListDict['b:itemList'] = dataElementDict
                        metadataDict[ 'b:partialOrder'] = relationListDict
                    myGridDataDocumentDict = { 'b:myGridDataDocument': metadataDict, '@key': port}
                    dataThingDic = {'b:dataThing': myGridDataDocumentDict}
                    dataThingDicString = xmltodict.unparse(dataThingDic, pretty=True)
                    dataThingDicString = dataThingDicString[ dataThingDicString.find('\n') + 1 : ]
                    fullDataThingStringList = fullDataThingStringList + dataThingDicString

            if fullDataThingStringList!="":
                baseDoc = baseDoc.replace("</b:dataThingMap>" , "\n" + fullDataThingStringList + "\n")
                baseDoc = baseDoc + "</b:dataThingMap>"

            return baseDoc

        except Exception as e:
            raise Exception('Error while generating Baclava string: ' + e.message)

