from RackSpaceClient import RackSpaceClient
from Exceptions import *
import simplejson
from json2pyo import RawMapper

class Server(RawMapper):
    def __init__(self, srv):
        RawMapper.__init__(self, srv)
        self.customMapper('state', "self.mapState()")
        self.clearProperty('status')
        self.clearProperty('progress')
        

    def mapState(self):
        """mapState custom mapper for state objects"""
        so = self.RawClass()
        if hasattr(self.resultObject, 'status'):
            setattr(so, 'status', self.resultObject.status)
        else:
            setattr(so, 'status', None)
            
        if hasattr(self.resultObject, 'progress'):
            setattr(so, 'progress', self.resultObject.progress)                
        else:
            setattr(so, 'progress', None)
        return so


class ServerImage(RawMapper):
    def fixProgress(self):
        if not hasattr(self.resultObject, 'progress'):
            return 0
        else:
            return self.resultObject.progress


class RackSpaceManager:
# TODO: add exception handling
    def __init__(self, user = '', key = ''):
        self.rsClient = RackSpaceClient(None, None)
    
    def ListServers(self, isDetail = False):
        if isDetail:
            method = "/servers/detail"
        else:
            method = "/servers"
        servers = self.rsClient.SendRequest(rType = "GET", method = method, data = None, params = None)
        serverList = []
        for server in simplejson.loads(servers['body'])['servers']:
            srv = Server(server)
            serverList.append(srv.getObject())
        return serverList



    def ListImages(self, isDetail = False):
        if isDetail:
            method = "/images/detail"
        else:
            method = "/images"
        images = self.rsClient.SendRequest(rType = "GET", method = method, data = None, params = None)
        imageList = []
        for img in simplejson.loads(images['body'])['images']:
            image = ServerImage(img)
            image.customMapper('progress', 'self.fixProgress()')
            imageList.append(image.getObject())
        return imageList

    def CreateServer(self, name, imageId, flavorId, metadata = None, personality = None):
        # Creates server, returns new object or throws exception if something wrong.

        # constructing request
        srv = {"name": name, "imageId": imageId, "flavorId": flavorId}
        if metadata is not None:
            srv["metadata"] = metadata
        if personality is not None:
            srv["personality"] = personality

        req = simplejson.dumps({"server": srv})

        # sending
        try:
            response = self.rsClient.SendRequest(rType="POST", method = "/servers", data = req, params = None)
        except RackSpaceException:
            raise
        # parsing response
# TODO: parse response, handle errors
        if response["code"] == 202:
            srv = Server(simplejson.loads(response['body'])['server'])
            srv.setAliasMap({'rootPassword': 'adminPass'})
            srv.makeAliasMap()
            return srv.getObject()
        raise RackSpaceException()


    def DeleteServer(self, serverId):
        # Delete specified by id server
        try:
            response = self.rsClient.SendRequest(rType="DELETE", method = "/servers/"+serverId, data = None, params = None)
        except RackSpaceException:
            raise
        if response["code"] != 202:
            # Something wrong
            raise RackSpaceException()
    
    def ListFlavors(self, isDetail = False):
        """Returns a list of flavors"""
        if isDetail:
            method = "/flavors/detail"
        else:
            method = "/flavors"
        flavors = self.rsClient.SendRequest(rType = "GET", method = method, data = None, params = None)
        flavorsList = []

        for flavor in simplejson.loads(flavors['body'])['flavors']:
            fl = RawMapper(flavor)
            flavorsList.append(fl.getObject())
        return flavorsList

    def UpdateServer(self, serverId, name = None, password = None):
        # Changes server name and root password.
        srv = {}
        if name is not None:
            srv["name"] = name
        if password is not None:
            srv["adminPass"] = password

        request = simplejson.dumps({"server": srv})

        try:
            response = self.rsClient.SendRequest(rType="PUT", method = "/servers/" + serverId, data = request, params = None)
        except RackSpaceException:
            raise
        if response["code"] != 204:
            # Error
            raise RackSpaceException()

    def RebootServer(self, serverId, hardReboot = False):
        # Reboot specified server
        rtype = "SOFT"
        if hardReboot:
            rtype = "HARD"

        req = {"reboot" : {"type": rtype}}
        request = simplejson.dumps(req)

        try:
            response = self.rsClient.SendRequest(rType="POST", method = "/servers/" + serverId + "/action", data = request, params = None)
        except RackSpaceException:
            raise
        if response["code"] != 202:
            # Error
            raise RackSpaceException()

    def CreateImage(self, serverId, name):
        # Create custom image from specified server
        req = {"image" : {"serverId": serverId, "name": name}}
        request = simplejson.dumps(req)

        try:
            response = self.rsClient.SendRequest(rType="POST", method = "/images", data = request, params = None)
        except RackSpaceException:
            raise
        if response["code"] != 202:
            # Error
            raise RackSpaceException()
        image = ServerImage(simplejson.loads(response['body'])['image'])
        image.customMapper('progress', 'self.fixProgress()')

        return image

    def DeleteImage(self, imageId):
        # Delete server image specified by id
        try:
            response = self.rsClient.SendRequest(rType="DELETE", method = "/images/"+imageId, data = None, params = None)
        except RackSpaceException:
            raise
        if response["code"] != 204:
            # Something wrong
            raise RackSpaceException()







