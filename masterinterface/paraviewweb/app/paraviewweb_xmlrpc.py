__author__ = 'Alfredo Saglimbeni a.saglimbeni@scsitaly.com'
from flask import Flask, g, jsonify
from flaskext.xmlrpc import XMLRPCHandler, Fault

import json
import math
import os
from time import time

# import paraview modules.
from paraview import simple, web, servermanager, web_helper
from vtkParaViewWebCorePython import vtkPVWebInteractionEvent
from vtkParaViewWebCorePython import vtkPVWebApplication
from raven.contrib.flask import Sentry
# =============================================================================
#
# Base class for any ParaView based protocol
#
# =============================================================================


class ParaViewWebProtocol(object):

    DISTANCE_FACTOR = 2.0
    CONTOUR_LINE_WIDTH = 2.0

    colorArrayName = None
    sof = None
    lookupTable = None
    srcObj = None
    bounds = None
    extent = None
    center = None
    centerExtent = None
    rep = None
    scalarRange = None
    imageData = None
    subgrid = None
    sliceMode = None
    meshSlice = None
    sphere = None
    surfaces = []

    def __init__(self):
        self.Application = vtkPVWebApplication()

        self.view = simple.GetRenderView()
        simple.Render()
        self.view.ViewSize = [800,800]
        self.view.Background = [0, 0, 0]
        self.view.OrientationAxesLabelColor = [0, 0, 0]
        simple.SetActiveView(self.view)
        self.reader = None
        # setup animation scene
        #self.scene = simple.GetAnimationScene()
        #simple.GetTimeTrack()
        #self.scene.PlayMode = "Snap To TimeSteps"

    def _extractVolumeImageData(self):
        if(self.reader.GetPointDataInformation().GetNumberOfArrays() == 0):
            print 'Error: no data information arrays'
            raise Exception('No data information arrays')

        self.imageData = self.reader.GetPointDataInformation().GetArray(0)
        self.colorArrayName = self.imageData.Name
        self.scalarRange = self.imageData.GetRange()
        self.bounds = self.reader.GetDataInformation().DataInformation.GetBounds()
        self.extent = self.reader.GetDataInformation().DataInformation.GetExtent()
        self.center = [(self.bounds[1] + self.bounds[0]) / 2.0,
                                     (self.bounds[3] + self.bounds[2]) / 2.0,
                                     (self.bounds[5] + self.bounds[4]) / 2.0]
        self.centerExtent = [(self.extent[1] + self.extent[0]) / 2.0,
                                                 (self.extent[3] + self.extent[2]) / 2.0,
                                                 (self.extent[5] + self.extent[4]) / 2.0]

    def _loadSurfaceWithProperties(self, fullpath):
        if not fullpath.endswith('.properties'):
            surfaceObj = simple.OpenDataFile(fullpath)
            self.surfaces.append(surfaceObj)
            rep = simple.Show()
            rep.Representation = 'Surface'

            # If a corresponding properties file exists, load it in
            # and apply the properties to the surface
            if os.path.isfile(fullpath+'.properties'):
                with open(fullpath+'.properties') as f:
                    lines = f.readlines()
                    for line in lines:
                        (property, value) = line.split(' ', 1)
                        if hasattr(rep, property):
                            value = json.loads(value.strip())
                            setattr(rep, property, value)
                        else:
                            print 'Skipping invalid property %s' % property

            print 'Loaded surface %s into scene' % fullpath

    def _sliceSurfaces(self, slice):
        if self.meshSlice is not None:
            simple.Delete(self.meshSlice)
            self.meshSlice = None

        for surface in self.surfaces:
            rep = simple.Show(surface)

            if self.sliceMode == 'XY Plane':
                origin = [0.0, 0.0, math.cos(math.radians(rep.Orientation[2]))*slice]
                normal = [0.0, 0.0, 1.0]
            elif self.sliceMode == 'XZ Plane':
                origin = [0.0, math.cos(math.radians(rep.Orientation[1]))*slice, 0.0]
                normal = [0.0, 1.0, 0.0]
            else:
                origin = [math.cos(math.radians(rep.Orientation[0]))*slice, 0.0, 0.0]
                normal = [1.0, 0.0, 0.0]

            simple.Hide(surface)
            self.meshSlice = simple.Slice(Input=surface, SliceType='Plane')
            simple.SetActiveSource(self.reader)

            self.meshSlice.SliceOffsetValues = [0.0]
            self.meshSlice.SliceType = 'Plane'
            self.meshSlice.SliceType.Origin = origin
            self.meshSlice.SliceType.Normal = normal
            meshDataRep = simple.Show(self.meshSlice)

            meshDataRep.Representation = 'Points'
            meshDataRep.LineWidth = self.CONTOUR_LINE_WIDTH
            meshDataRep.PointSize = self.CONTOUR_LINE_WIDTH
            meshDataRep.AmbientColor = rep.DiffuseColor
            meshDataRep.Orientation = rep.Orientation

        simple.SetActiveSource(self.reader)


    def mapIdToProxy(self, id):
        """
        Maps global-id for a proxy to the proxy instance. May return None if the
        id is not valid.
        """
        id = int(id)
        if id <= 0:
            return None
        return simple.servermanager._getPyProxy(simple.servermanager.ActiveConnection.Session.GetRemoteObject(id))

    def getView(self, vid):
        """
        Returns the view for a given view ID, if vid is None then return the
        current active view.
        :param vid: The view ID
        :type vid: str
        """

        #view = self.mapIdToProxy(vid)
        view = False
        if not view:
            view = simple.GetActiveView()
        if not view:
            raise Exception("no view provided: " + vid)

        return view

    def setApplication(self, app):
        self.Application = app

    def getApplication(self):
        return self.Application

    # =============================================================================
    #
    # Handle Mouse interaction on any type of view
    #
    # =============================================================================

    def mouseInteraction(self, event):
        """
        RPC Callback for mouse interactions.
        """
        view = self.getView(event['view'])

        buttons = 0
        if event["buttonLeft"]:
            buttons |= vtkPVWebInteractionEvent.LEFT_BUTTON;
        if event["buttonMiddle"]:
            buttons |= vtkPVWebInteractionEvent.MIDDLE_BUTTON;
        if event["buttonRight"]:
            buttons |= vtkPVWebInteractionEvent.RIGHT_BUTTON;

        modifiers = 0
        if event["shiftKey"]:
            modifiers |= vtkPVWebInteractionEvent.SHIFT_KEY
        if event["ctrlKey"]:
            modifiers |= vtkPVWebInteractionEvent.CTRL_KEY
        if event["altKey"]:
            modifiers |= vtkPVWebInteractionEvent.ALT_KEY
        if event["metaKey"]:
            modifiers |= vtkPVWebInteractionEvent.META_KEY

        pvevent = vtkPVWebInteractionEvent()
        pvevent.SetButtons(buttons)
        pvevent.SetModifiers(modifiers)
        pvevent.SetX(event["x"])
        pvevent.SetY(event["y"])
        #pvevent.SetKeyCode(event["charCode"])
        retVal = self.getApplication().HandleInteractionEvent(view.SMProxy, pvevent)
        del pvevent
        return retVal

    # =============================================================================
    #
    # Basic 3D Viewport API (Camera + Orientation + CenterOfRotation
    #
    # =============================================================================

    def resetCamera(self, view):
        """
        RPC callback to reset camera.
        """
        view = self.getView(view)
        simple.ResetCamera(view)
        try:
            view.CenterOfRotation = view.CameraFocalPoint
        except:
            pass

        self.getApplication().InvalidateCache(view.SMProxy)
        return view.GetGlobalIDAsString()

    def updateOrientationAxesVisibility(self, view, showAxis):
        """
        RPC callback to show/hide OrientationAxis.
        """
        view = self.getView(view)
        view.OrientationAxesVisibility = (showAxis if 1 else 0);

        self.getApplication().InvalidateCache(view.SMProxy)
        return view.GetGlobalIDAsString()

    def updateCenterAxesVisibility(self, view, showAxis):
        """
        RPC callback to show/hide CenterAxesVisibility.
        """
        view = self.getView(view)
        view.CenterAxesVisibility = (showAxis if 1 else 0);

        self.getApplication().InvalidateCache(view.SMProxy)
        return view.GetGlobalIDAsString()

    def updateCamera(self, view_id, focal_point, view_up, position):
        view = self.getView(view_id)

        view.CameraFocalPoint = focal_point
        view.CameraViewUp = view_up
        view.CameraPosition = position
        self.getApplication().InvalidateCache(view.SMProxy)

    # =============================================================================
    #
    # Provide Image delivery mechanism
    #
    # =============================================================================

    def stillRender(self, options):
        """
        RPC Callback to render a view and obtain the rendered image.
        """
        beginTime = int(round(time() * 1000))
        view = self.getView(int(options["view"]))
        #view = self.view
        size = [view.ViewSize[0], view.ViewSize[1]]
        if options and options.has_key("size"):
            size = options["size"]
            view.ViewSize = [int(size[0]),int(size[1])]
        t = 0
        if options and options.has_key("mtime"):
            t = int(options["mtime"])
        quality = 100
        if options and options.has_key("quality"):
            quality = int(options["quality"])
        localTime = 0
        if options and options.has_key("localTime"):
            localTime = int(options["localTime"])
        reply = {}
        app = self.getApplication()
        reply["image"] = app.StillRenderToString(view.SMProxy, t, quality)
        reply["stale"] = app.GetHasImagesBeingProcessed(view.SMProxy)
        reply["mtime"] = app.GetLastStillRenderToStringMTime()
        reply["size"] = [view.ViewSize[0], view.ViewSize[1]]
        reply["format"] = "jpeg;base64"
        reply["global_id"] = view.GetGlobalIDAsString()
        reply["localTime"] = localTime

        endTime = int(round(time() * 1000))
        reply["workTime"] = (endTime - beginTime)
        return reply

    # =============================================================================
    #
    # Provide Geometry delivery mechanism (WebGL)
    #
    # =============================================================================

    def getSceneMetaData(self, view_id):
        view  = self.getView(view_id)
        data = self.getApplication().GetWebGLSceneMetaData(view.SMProxy)
        return data

    def getWebGLData(self, view_id, object_id, part):
        view  = self.getView(view_id)
        data = self.getApplication().GetWebGLBinaryData(view.SMProxy, str(object_id), part-1)
        return data

    # =============================================================================
    #
    # Time management
    #
    # =============================================================================

    def updateTime(self,action):
        view = simple.GetRenderView()
        animationScene = simple.GetAnimationScene()
        currentTime = view.ViewTime

        if action == "next":
            animationScene.GoToNext()
            if currentTime == view.ViewTime:
                animationScene.GoToFirst()
        if action == "prev":
            animationScene.GoToPrevious()
            if currentTime == view.ViewTime:
                animationScene.GoToLast()
        if action == "first":
            animationScene.GoToFirst()
        if action == "last":
            animationScene.GoToLast()

        return view.ViewTime

    def openFile(self, file):
        id = ""
        print "Apertura file \n"
        if self.reader:
            try:
                simple.Delete(self.reader)
            except Exception, e:
                self.reader = None
        try:
            print "Lettura file \n"
            self.reader = simple.OpenDataFile(file)
            simple.Show()
            simple.Render()
            simple.ResetCamera()
            id = self.reader.GetGlobalIDAsString()
            self.rep = simple.GetDisplayProperties()
        except Exception, e:
            sentry.captureException()
            self.reader = None
        print "id:"+id
        return id

    def openFileFromPath(self, file):
        print file+"\n"
        file = os.path.join(self.pathToList, file)
        return self.openFile(file)

    def listFiles(self):
        nodeTree = {}
        rootNode = { "data": "/", "children": [] , "state" : "open"}
        nodeTree[self.pathToList] = rootNode
        for path, directories, files in os.walk(self.pathToList):
            parent = nodeTree[path]
            for directory in directories:
                child = {'data': directory , 'children': [], "state" : "open", 'metadata': {'path': 'dir'}}
                nodeTree[path + '/' + directory] = child
                parent['children'].append(child)
                if directory == 'vtk':
                    child['state'] = 'closed'
            for filename in files:
                child = {'data': { 'title': filename, 'icon': '/'}, 'children': [], 'metadata': {'path': path + '/' + filename}}
                nodeTree[path + '/' + filename] = child
                parent['children'].append(child)
        return rootNode


    # =============================================================================
    #
    # Time management
    #
    # =============================================================================

    def setSliceMode(self, sliceMode):
        view = simple.GetRenderView()
        if type(sliceMode) is unicode:
            sliceMode = sliceMode.encode('ascii', 'ignore')

        if(sliceMode == 'XY Plane'):
            sliceNum = int(math.floor(self.centerExtent[2]))
            cameraParallelScale = max(self.bounds[1] - self.bounds[0],
                                                                self.bounds[3] - self.bounds[2]) / 2.0
            cameraPosition = [self.center[0], self.center[1], self.bounds[4] - 10]
            maxSlices = self.extent[5] - self.extent[4]
            cameraViewUp = [0, -1, 0]
        elif(sliceMode == 'XZ Plane'):
            sliceNum = int(math.floor(self.centerExtent[1]))
            cameraParallelScale = max(self.bounds[1] - self.bounds[0],
                                                                self.bounds[5] - self.bounds[4]) / 2.0
            maxSlices = self.extent[3] - self.extent[2]
            cameraPosition = [self.center[0], self.bounds[3] + 10, self.center[2]]
            cameraViewUp = [0, 0, 1]
        elif(sliceMode == 'YZ Plane'):
            sliceNum = int(math.floor(self.centerExtent[0]))
            cameraParallelScale = max(self.bounds[3] - self.bounds[2],
                                                                self.bounds[5] - self.bounds[4]) / 2.0
            maxSlices = self.extent[1] - self.extent[0]
            cameraPosition = [self.bounds[1] + 10, self.center[1], self.center[2]]
            cameraViewUp = [0, 0, 1]
        else:
            print 'Error: invalid slice mode %s' % sliceMode
            raise Exception('Error: invalid slice mode %s' % sliceMode)

        #view.CameraParallelScale = cameraParallelScale
        view.CameraViewUp = cameraViewUp
        view.CameraPosition = cameraPosition

        self.rep.Slice = sliceNum
        self.rep.SliceMode = sliceMode

        self.sliceMode = sliceMode
        # TODO calculate slice plane origin for surfaces!!!
        self._sliceSurfaces(sliceNum)
        simple.Render()
        return {'slice': sliceNum,
                        'maxSlices': maxSlices,
                        'cameraParallelScale': cameraParallelScale}

    def changeSlice(self, sliceNum):
        self.rep.Slice = sliceNum
        self._sliceSurfaces(sliceNum)
        simple.Render()

    def changeWindow(self, points):
        points = [points[0], 0, 0, 0, points[1], 1, 1, 1]
        self.lookupTable.RGBPoints = points
        simple.Render()

    def sliceRender(self, sliceMode):
        view = simple.GetRenderView()

        self._extractVolumeImageData()

        (midx, midy, midz) = (self.center[0], self.center[1], self.center[2])
        (lenx, leny, lenz) = (self.bounds[1] - self.bounds[0], self.bounds[3] - self.bounds[2], self.bounds[5] - self.bounds[4])

        maxDim = max(lenx, leny, lenz)

        # Adjust camera properties appropriately
        view.Background = [0, 0, 0]
        view.CameraFocalPoint = self.center
        view.CenterOfRotation = self.center
        view.CenterAxesVisibility = False
        view.OrientationAxesVisibility = False
        view.CameraParallelProjection = True

        # Configure data representation
        rgbPoints = [self.scalarRange[0], 0, 0, 0, self.scalarRange[1], 1, 1, 1]
        self.lookupTable = simple.GetLookupTableForArray(self.colorArrayName, 1)
        self.lookupTable.RGBPoints = rgbPoints
        self.lookupTable.ScalarRangeInitialized = 1.0
        self.lookupTable.ColorSpace = 0    # 0 corresponds to RGB

        self.rep.ColorArrayName = self.colorArrayName
        self.rep.Representation = 'Slice'
        self.rep.LookupTable = self.lookupTable

        sliceInfo = self.setSliceMode(sliceMode)

        simple.Show()
        simple.Render()

        return {'scalarRange': self.scalarRange,
                'bounds': self.bounds,
                'extent': self.extent,
                'center': self.center,
                'sliceInfo': sliceInfo,
                'maxdim': [lenx, leny, lenz]}

    def volumeRender(self):
        view = simple.GetRenderView()
        self._extractVolumeImageData()
        (lenx, leny, lenz) = (self.bounds[1] - self.bounds[0],
                                                    self.bounds[3] - self.bounds[2],
                                                    self.bounds[5] - self.bounds[4])
        (midx, midy, midz) = (self.center[0], self.center[1], self.center[2])
        maxDim = max(lenx, leny, lenz)
        # Adjust camera properties appropriately
        view.CameraFocalPoint = self.center
        view.CenterOfRotation = self.center
        view.CameraPosition = [midx - self.DISTANCE_FACTOR * maxDim, midy, midz]
        view.CameraViewUp = [0, 0, 1]

        # Create RGB transfer function
        rgbPoints = [self.scalarRange[0], 0, 0, 0, self.scalarRange[1], 1, 1, 1]
        self.lookupTable = simple.GetLookupTableForArray(self.colorArrayName, 1)
        self.lookupTable.RGBPoints = rgbPoints
        self.lookupTable.ScalarRangeInitialized = 1.0
        self.lookupTable.ColorSpace = 0    # 0 corresponds to RGB

        # Create opacity transfer function
        sofPoints = [self.scalarRange[0], 0, 0.5, 0,
                     self.scalarRange[1], 1, 0.5, 0]
        self.sof = simple.CreatePiecewiseFunction()
        self.sof.Points = sofPoints

        self.rep.ColorArrayName = self.colorArrayName
        self.rep.Representation = 'Volume'
        self.rep.ScalarOpacityFunction = self.sof
        self.rep.LookupTable = self.lookupTable
        simple.Show()
        simple.Render()

        return {'scalarRange': self.scalarRange,
                        'bounds': self.bounds,
                        'extent': self.extent,
                        'sofPoints': sofPoints,
                        'rgbPoints': rgbPoints}

    def updateSof(self, sofPoints):
        # costruire l'interfaccia con Jplot
        self.sof = simple.CreatePiecewiseFunction()
        self.sof.Points = sofPoints
        self.rep.ScalarOpacityFunction = self.sof
        simple.Render()

    def updateColorMap(self, rgbPoints):
        self.lookupTable = simple.GetLookupTableForArray(self.colorArrayName, 1)
        self.lookupTable.RGBPoints = rgbPoints
        self.rep.LookupTable = self.lookupTable

    def extractSubgrid(self, bounds):

        #bounds is an array of 6 element  [x0,x1,y0,y1,z0,z1]
        # costruire l'interfaccia con il tris di slider

        if(self.subgrid is not None):
            simple.Delete(self.subgrid)
        simple.SetActiveSource(self.srcObj)
        self.subgrid = simple.ExtractSubset()
        self.subgrid.VOI = bounds
        simple.SetActiveSource(self.subgrid)

        self.rep = simple.Show()
        self.rep.ScalarOpacityFunction = self.sof
        self.rep.ColorArrayName = self.colorArrayName
        self.rep.Representation = 'Volume'
        self.rep.SelectionPointFieldDataArrayName = self.colorArrayName
        self.rep.LookupTable = self.lookupTable

        simple.Hide(self.srcObj)
        simple.SetActiveSource(self.subgrid)
        simple.Render()

    def cameraPreset(self, direction):
        view = simple.GetRenderView()
        (midx, midy, midz) = (self.center[0], self.center[1], self.center[2])
        (lenx, leny, lenz) = (self.bounds[1] - self.bounds[0], self.bounds[3] - self.bounds[2], self.bounds[5] - self.bounds[4])
        maxDim = max(lenx, leny, lenz)

        view.CameraFocalPoint = self.center
        view.CenterOfRotation = self.center
        view.CameraViewUp = [0, 0, 1]

        if(direction == '+x'):
            view.CameraPosition = [midx - self.DISTANCE_FACTOR * maxDim, midy, midz]
        elif(direction == '-x'):
            view.CameraPosition = [midx + self.DISTANCE_FACTOR * maxDim, midy, midz]
        elif(direction == '+y'):
            view.CameraPosition = [midx, midy - self.DISTANCE_FACTOR * maxDim, midz]
        elif(direction == '-y'):
            view.CameraPosition = [midx, midy + self.DISTANCE_FACTOR * maxDim, midz]
        elif(direction == '+z'):
            view.CameraPosition = [midx, midy, midz - self.DISTANCE_FACTOR * maxDim]
            view.CameraViewUp = [0, 1, 0]
        elif(direction == '-z'):
            view.CameraPosition = [midx, midy, midz + self.DISTANCE_FACTOR * maxDim]
            view.CameraViewUp = [0, 1, 0]
        else:
            print "Invalid preset direction: %s" % direction

        simple.Render()


    def _getLutId(self, name, number_of_components):
        return "%s_%d" % (name, number_of_components)

    def registerArray(self, name, number_of_components, range):
        key = self._getLutId(name, number_of_components)
        view = simple.GetActiveView()
        if self.range.has_key(key):
            minValue = min(range[0], self.luts[key].RGBPoints[0])
            maxValue = max(range[1], self.luts[key].RGBPoints[-4])
            self.range[key] = [minValue, maxValue]
            self.luts[key].RGBPoints = [minValue, 0, 0, 1, maxValue, 1, 0, 0]
            self.luts[key].VectorMode = 'Magnitude'
            self.luts[key].VectorComponent = 0
            self.luts[key].ColorSpace = 'HSV'
        else:
            self.range[key] = range
            self.luts[key] = simple.GetLookupTableForArray(name, number_of_components)

            # Setup default config
            self.luts[key].RGBPoints  = [range[0], 0, 0, 1, range[1], 1, 0, 0]
            self.luts[key].VectorMode = 'Magnitude'
            self.luts[key].VectorComponent = 0
            self.luts[key].ColorSpace = 'HSV'

            self.scalarbars[key] = simple.CreateScalarBar(LookupTable=self.luts[key])
            self.scalarbars[key].Title = name
            self.scalarbars[key].Visibility = 0
            self.scalarbars[key].Enabled = 0

            # Add scalar bar to the view
            if view:
                view.Representations.append(self.scalarbars[key])

    def _extractLutArray(self):
        data = self.reader.GetPointDataInformation()
        size = data.GetNumberOfArrays()
        self.luts = {}
        self.scalarbars = {}
        self.range = {}
        for i in range(size):
            array = data.GetArray(i)
            name = array.Name
            nbComp = array.GetNumberOfComponents()
            dataRange = [0.0, 1.0]
            if nbComp != 1:
                dataRange = array.GetRange(-1)
            else:
                dataRange = array.GetRange(0)

            self.registerArray(name, nbComp, dataRange)

    def _getScalarbarVisibility(self):
        status = {}
        for key in self.scalarbars.keys():
            status[key] = {
                'lutId': key,
                'name': key[0:-2],
                'size': int(key[-1]),
                'enabled': self.scalarbars[key].Visibility}
        return status

    def enableScalarBarFromId(self, id, show):
        if self.scalarbars.has_key(id):
            self.scalarbars[id].Visibility = show
            self.scalarbars[id].Enabled = show
            self.scalarbars[id].Repositionable = show
            self.scalarbars[id].Selectable = show

    def enableLutFromId(self, id):

        self.rep.LookupTable = self.luts[id]
        self.rep.ColorArrayName = self.scalarbars[id].Title
        simple.Show()
        simple.Render()

    def surfaceRender(self):
        self._extractVolumeImageData()
        self.bounds = self.reader.GetDataInformation().DataInformation.GetBounds()
        self.center = [(self.bounds[1] + self.bounds[0]) / 2.0, (self.bounds[3] + self.bounds[2]) / 2.0,
                       (self.bounds[5] + self.bounds[4]) / 2.0]

        self.cameraPreset('+x')
        self._extractLutArray()
        self.rep.Representation = 'Surface'

        nbPoints = self.reader.GetDataInformation().GetNumberOfPoints()
        nbCells = self.reader.GetDataInformation().GetNumberOfCells()

        simple.Show()
        simple.Render()
        return {'bounds': self.bounds,
                'nbPoints': nbPoints,
                'nbCells': nbCells,
                'scalarbarVisibility': self._getScalarbarVisibility()}
########################################
#### FLASK WRAPING OF PARAVIEW CLASS ###
########################################

pvw_protocol = None

app = Flask(__name__)

handler = XMLRPCHandler('api')
handler.connect(app, '/api')

app.config['SENTRY_DSN'] = 'http://1c3c7d624a8a497589d27e007fb8f35f:a7dc3fa664474ddeb52ee8e6229f8cb3@sentry.vph-share.eu/5'
sentry = Sentry(app)

@handler.register
def ready():
    return True

@handler.register
def pvw_call_method(method=None, args="[]"):
    global pvw_protocol

    pvw_obj = pvw_protocol
    if pvw_obj is None:
        pvw_obj = g.pvw_protocol = ParaViewWebProtocol()

    method_to_call = getattr(pvw_obj, method)
    if not method_to_call:
        return None
    try:
        result = method_to_call(*json.loads(args))
        if type(result) is dict:
            return json.dumps(result)
        else:
            return json.dumps(result)
    except Exception, e:
        sentry.captureException()
        print "Errore"
        print e

if __name__ == "__main__":
    global pvw_protocol
    import argparse

    parser = argparse.ArgumentParser(description='Development Server Help')
    parser.add_argument("-d", "--debug", action="store_true", dest="debug_mode",
                        help="run in debug mode (for use with PyCharm)", default=False)
    parser.add_argument("-p", "--port", dest="port",
                        help="port of server (default:%(default)s)", type=int, default=5000)

    cmd_args = parser.parse_args()
    app_options = {"port": cmd_args.port}

    ParaViewWebProtocol.pathToList = "/app/vphshare-prod/vphshare/masterinterface/data_paraview/"

    pvw_protocol = ParaViewWebProtocol()

    if cmd_args.debug_mode:
        app_options["debug"] = True
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False

    app.run(**app_options)
