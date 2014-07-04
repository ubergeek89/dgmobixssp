# ADSERVER Request Format
# INSTALL - TORNADO, GEOIP
# SET SERVER TIMEZONE to IST

from wurfl import devices
from pywurfl.algorithms import TwoStepAnalysis
from random import choice
import random
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
import pygeoip

from urlparse import urlparse
from tornado.web import asynchronous
import tornado.options
from tornado.options import define, options

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if self.request.path == "/":
            self.write("Nothing special here. Go <a href='http://google.com'>here</a>")	
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
	self.set_header("Cache-Control","no-cache")
	self.set_header("Pragma","no-cache")      
        placementId = int(self.get_argument('plid'))
        supplyPartnerId = int(self.get_argument('paid'))
        width = int(self.get_argument('w'))
        height = int(self.get_argument('h'))
        
	ta = self.request.query.split("&red=")
	thirdPartyUrl = ta[1]
	if thirdPartyUrl=="CLICK_MACRO":
	  thirdPartyUrl=""

	if width==300 and height==250:
	  demandPartnerId=26
	  campaignId=36
	  creativeId=9
	  creativeUrl="http://rtbcreative.dgmobix.com/creatives/jawani_pack_99_300x250.gif"
	  destinationUrl="http://clk.dgmobix.com/clks/clk_t.php?tagid=141680973__cb=INSERT_RANDOM_NUMBER_HERE"
	  timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	  randomno = random.randrange(1000000,9999999)
	  clickUrl=thirdPartyUrl+"http://rtbserver.dgmobix.com/click?paid="+str(supplyPartnerId)+"&plid="+str(placementId)+"&caid="+str(campaignId)+"&crid="+str(creativeId)+"&dpid="+str(demandPartnerId)+"&r="+str(randomno)+"&red="+destinationUrl
	  tagCode="<a href='"+clickUrl+"'><img src='"+creativeUrl+"'></a>"

	  #search_algorithm = TwoStepAnalysis(devices)
	  #device = devices.select_ua(self.request.headers['User-Agent'], search=search_algorithm)
	  #print device.brand_name

	    
	  message=json.dumps({"message":"impression",
	      "placementId":placementId,
	      "supplyPartnerId":supplyPartnerId,
	      "demandPartnerId":demandPartnerId,
	      "campaign":campaignId,
	      "creativeId":creativeId,
	      "timestamp":timestamp,
	      "ipaddress":self.request.headers['X-Forwarded-For'],
	      "useragent":self.request.headers['User-Agent'],
	      "revenue":0,
	      "cost":0.83
	  })
	  self.sendToLogAgent(message)
	  self.write(tagCode)
	  
	self.finish()	  

    def click(self,info):
        placementId = int(self.get_argument('plid'))
        supplyPartnerId = int(self.get_argument('paid'))
        campaignId=int(self.get_argument('caid'))
        creativeId=int(self.get_argument('crid'))        
        demandPartnerId=int(self.get_argument('dpid'))        
	ta = self.request.query.split("&red=")
	redirectUrl = ta[1]
	timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")	
	message=json.dumps({"message":"click",
	    "placementId":placementId,
	    "supplyPartnerId":supplyPartnerId,
	    "demandPartnerId":demandPartnerId,
	    "campaignId":campaignId,
	    "creativeId":creativeId,
	    "timestamp":timestamp,
	    "revenue":0.01,
	    "cost":0
	})
	self.sendToLogAgent(message)
	self.redirect(redirectUrl)
        
    def visit(self,info):
        self.write("i am ok - visit")

    def install(self,info):
        self.write("i am ok - install")
        
    def download(self,info):
        self.write("i am ok - download")
        
    def healthcheck(self,info):
        self.write("i am ok - healthcheck")
            
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
#gi = GeoIP.open("/usr/share/GeoIP/GeoIPISP.dat",GeoIP.GEOIP_STANDARD)
#gi_city = GeoIP.open("/usr/share/GeoIP/GeoIPCityin.dat",GeoIP.GEOIP_STANDARD)


if __name__ == "__main__":
    print "starting server name="+options.name
    #print "refreshing cache first time"
    #refreshCache()
    tornado.options.parse_command_line()
    server_settings = {
	"xheaders" : True,
    }    
    application.listen(options.port, **server_settings)
   # tornado.ioloop.PeriodicCallback(refreshCache, options.refreshCache).start()
    tornado.ioloop.IOLoop.instance().start()