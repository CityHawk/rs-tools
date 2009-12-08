import unittest
from json2pyo import RawMapper
import inspect
from pprint import pprint

class TestObjectCreation(unittest.TestCase):
    def setUp(self):
        self.sampleObject = {'a': 1, 
                             'b': '2', 
                             'c': {'c1': 'foo', 
                                   'c2': 'bar'}, 
                             'd': "I don't need it!"}

    def testCoreCreation1(self):
        o = RawMapper(self.sampleObject).getObject()
        assert o.a == 1
    
    def testCoreCreation2(self):
        o = RawMapper(self.sampleObject).getObject()
        pprint(inspect.getmembers(o.c))
        assert o.c.c2 == 'bar'

if __name__ == "__main__":
    unittest.main()
