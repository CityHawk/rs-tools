#!/usr/bin/env python
import ConfigParser, os, sys
import urllib
import urlparse
import inspect
from pprint import pprint
from httplib  import HTTPSConnection, HTTPConnection, HTTPException

class BillingRSClient:
    
    headers = {'Accept': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
           'Content-Type': 'application/x-www-form-urlencoded',
           'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.30 Safari/532.5'}

    host = 'manage.rackspacecloud.com'
    cookie = ''
    
    def __init__(self):
        """Reads config file and authenticates"""
        
        config = ConfigParser.ConfigParser()
        config.read(os.path.expanduser("~/.rackspacerc"))
        if not config.has_section('web'):
            print "No web part defined in config file!"
            sys.exit(1)
        self.login = config.get('web', 'login')
        self.passwd = config.get('web', 'passwd')
    
    def authenticate(self):
        """authenticates to the web interface and sets cookie"""
        self.cookie = (self.makeRequest(rtype='GET', rurl='/pages/Login.jsp'))[0].getheader('set-cookie')
        self.headers['set-cookie'] = self.cookie
        self.headers['cookie'] = self.cookie
        self.makeRequest(rtype='POST', rurl='/Login.do', rparams=urllib.urlencode({'username': self.login, 'password': self.passwd}), rheaders=self.headers)


    def makeRequest(self,rtype, rurl, rparams='', rheaders={}):
        """makeRequest is a wrapper to do HTTPRequest"""
        try:
            conn = HTTPSConnection(self.host, '443')
            conn.request(rtype, rurl, rparams, headers=rheaders)
            response = conn.getresponse()
            body = response.read()
        except Exception, e:
            raise e
        finally:
            conn.close()
        return response, body

    def getBillingInfo(self):
        """This makes a deal!"""
        rawrespdata = self.makeRequest(rtype = 'GET', rurl = '/CloudServers/ViewUsageReports.do', rheaders = self.headers)
        rawtabdata = None
        for l in (rawrespdata[1]).split('\n'):
            if 'tableData0' in l:
                rawtabdata = l

        if rawtabdata:
            rawtabdata = rawtabdata.replace("\\\"", '\"')
            rawtabdata = rawtabdata.lstrip(' ')
            rawtabdata = rawtabdata.lstrip('tableData0:')
            rawtabdata = rawtabdata.lstrip('\"')
            rawtabdata = rawtabdata.rstrip("\",")
            tdict = eval(rawtabdata)
            odict = []
            for d in tdict['rows']:
                o = type('empty', (object,), {})()
                setattr(o,'name',d[0])
                setattr(o,'diskspace',int(d[1]))
                setattr(o,'bandwidth', type('empty', (object,), {})())
                setattr(o.bandwidth, 'inGB', float(d[2]))
                setattr(o.bandwidth, 'outGB', float(d[3]))
                setattr(o,'uptime',d[4])
                setattr(o,'charges',float(d[5].lstrip('$')))
                odict.append(o)
            return odict
        else:
            return None
