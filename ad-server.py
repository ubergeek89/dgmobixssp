# ADSERVER Request Format
#INSTALL - TORNADO, GEOIP
# SET SERVER TIMEZONE to IST

from random import choice
import time
import hashlib
import re
import json
import datetime
import base64
import sys
import zlib
import urllib
import uuid
import tornado.ioloop
import tornado.web
import tornado.httpclient
import GeoIP

from urlparse import urlparse
from tornado.web import asynchronous
import tornado.options
from tornado.options import define, options

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if self.request.path == "/serve":
            self.serve(self.request.query)
        if self.request.path == "/click":
            self.click(self.request.query)
        if self.request.path == "/visit":
            self.visit(self.request.query)
        if self.request.path == "/install":
            self.install(self.request.query)
        if self.request.path == "/download":
            self.download(self.request.query)
        if self.request.path == "/healthcheck":
            self.healthcheck(self.request.query)
            
    def serve(self,info):
        self.write("i am ok")

    def click(self,info):
        self.write("i am ok")

    def visit(self,info):
        self.write("i am ok")

    def install(self,info):
        self.write("i am ok")
        
    def download(self,info):
        self.write("i am ok")
        
    def healthcheck(self,info):
        self.write("i am ok")
            
    def sendToLogAgent(self,message):
	print message
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch('http://localhost:9000/access', method='POST',body=message,callback=None)

def refreshCache():
    global adIndex
    http_client = tornado.httpclient.HTTPClient()
    try:
        response = http_client.fetch("http://terminal.impulse01.com:5003/adIndex")
        invertedIndex=json.loads(response.body)
    except:
        invertedIndex=dict()
    adIndex=invertedIndex    

define("port", default=8888, help="run on the given port", type=int)
define("name", default="noname", help="name of the server")
define("refreshCache", default=5000, help="millisecond interval between cache refresh", type=int)

application = tornado.web.Application([(r".*", MainHandler),])
adIndex = dict()
gi = GeoIP.open("/usr/share/GeoIP/GeoIPISP.dat",GeoIP.GEOIP_STANDARD)
gi_city = GeoIP.open("/usr/share/GeoIP/GeoIPCityin.dat",GeoIP.GEOIP_STANDARD)


if __name__ == "__main__":
    print "starting server name="+options.name
    print "refreshing cache first time"
    refreshCache()
    tornado.options.parse_command_line()
    server_settings = {
	"xheaders" : True,
    }    
    application.listen(options.port, **server_settings)
    tornado.ioloop.PeriodicCallback(refreshCache, options.refreshCache).start()
    tornado.ioloop.IOLoop.instance().start()