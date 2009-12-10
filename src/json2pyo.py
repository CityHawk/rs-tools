#!/usr/bin/python
             
class RawMapper:
    class RawClass:
        pass
    
    aliasMap=None
    
    def __init__(self, inDict, mapHash = None):
        """Base class to map Dict-from-JSON object to Python object"""
        self.resultObject = self.RawClass()
        self.makeItAProperty(self.resultObject, inDict) 
        if mapHash:
            self.setAliasMap(mapHash)
            self.makeAliasMap()

    def setAliasMap(self, mapHash):
        """setAliasMap used to define property aliases
        mapHash is a hash like {'property': 'goto'}
        """
        self.aliasMap = mapHash

    def makeItAProperty(self, obj, inDict):
        """makeItAProperty core method"""
        for i in inDict:
            if type(inDict[i]) is dict:
                to = self.RawClass()
                self.makeItAProperty(to, inDict[i])
                setattr(obj, i, to)
            else:
                setattr(obj, i, inDict[i])

    def makeAliasMap(self):
        """makeAliasMap used to map properties to properties"""
        for k in self.aliasMap:
            v = self.aliasMap[k]
            if hasattr(self.resultObject,v):
                setattr(self.resultObject, k, getattr(self.resultObject,v))

    def customMapper(self, propAlias, fn):
        """customMapper will call function to map property to a customMethod"""
        setattr(self.resultObject, propAlias,eval(fn))

    def clearProperty(self, prop):
        """clearProperty used to remap property to smth else"""
        if hasattr(self.resultObject, prop):
            delattr(self.resultObject, prop)

    def getObject(self):
        """getObject pushes RTR object"""
        return self.resultObject
