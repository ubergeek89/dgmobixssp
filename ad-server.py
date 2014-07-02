# ADSERVER Request Format
# IMPRESSION - http://rtbidder.impulse01.com/serve?{Base64-Encoded-Params}|||{Encrypted-Price}|||{Third-Party-Redirect-Url}
# CLICK - http://rtbidder.impulse01.com/click?{Base64-Encoded-Params}|||{Redirect-Url}
# SEGMENT - http://rtbidder.impulse01.com/segment?group={GroupId}
# Copyright - Impulse Media Pvt. Ltd.

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
	try:
	  global gi
	  global gi_city
	  self.set_header("Cache-Control","no-cache")
	  self.set_header("Pragma","no-cache")      
	  params = self.get_argument('info')
	  newParams = params.replace("-","+").replace("_","/")
	  newParams = newParams + '=' * (4 - len(newParams) % 4)
	  args = json.loads(base64.b64decode(newParams))
	  encrPrice = self.get_argument('p')
	  random = self.get_argument('r')

	  #No banner ID passed. This means this is a direct ad code. Whatever it is, decide the banner first and update the arguments.
	  if not args.has_key("bid"):
	      randomBannerId = choice(adIndex['banners:'+str(args['cid'])+':'+str(args['w'])+':'+str(args['h'])])
	      args['bid']=randomBannerId
	      del args['w']
	      del args['h']
	  
	  ip = self.request.remote_ip
	  isp = gi.org_by_name(ip)
	  gir = gi_city.record_by_name(ip)
	      
	  if not args.has_key('s'):
	      args['s']=gir["region_name"]

	  if not args.has_key('c'):
	      args['c']=gir["city"]

	  if not args.has_key('country'):
	      args['country']=gir["country_name"]

	  #Here we assume that the third party URL being passed is not URL Escaped. Hence split by &red=
	  ta = self.request.query.split("&red=")
	  thirdPartyUrl = ta[1]
	  if args['e']!="direct":
	    thirdPartyUrl=""
	    
	  ip = self.request.remote_ip
	  
	  #If imp_uid is not set, we are seeing the user for first time. Set new imp_uid
	  imp_uid = self.get_cookie("imp_uid",default=False)
	  if imp_uid == False:
	      imp_uid = str(uuid.uuid4())
	      self.set_cookie("imp_uid",imp_uid,expires_days=365)

	  args['imp_uid']=imp_uid
	  impressionId=str(uuid.uuid4())
	  args['impressionId']=impressionId

	  if adIndex.has_key('c:'+str(args['cid'])+':b:'+str(args['bid'])+':url'):
	    if len(adIndex['c:'+str(args['cid'])+':b:'+str(args['bid'])+':url'])>0:
	      url = adIndex['c:'+str(args['cid'])+':b:'+str(args['bid'])+':url']
	    else:
	      url = adIndex['c:'+str(args['cid'])+':url']	    
	  else : 
	      url = adIndex['c:'+str(args['cid'])+':url']

	  if len(thirdPartyUrl) == 0:
	      finalUrl = "http://rtbidder.impulse01.com/click?id="+impressionId+"&cid="+str(args['cid'])+"&red="+url
	  else:
	      finalUrl = thirdPartyUrl+urllib.quote("http://rtbidder.impulse01.com/click?id="+impressionId+"&cid="+str(args['cid'])+"&red="+url)
	  
	  if adIndex.has_key('b:'+str(args['bid'])+':url'):
	      creativeUrl = adIndex['b:'+str(args['bid'])+':url']
	      
	  width = adIndex['b:'+str(args['bid'])+':width']
	  height = adIndex['b:'+str(args['bid'])+':height']
	      
	  if adIndex['b:'+str(args['bid'])+':type'] == 1:
	      self.write('<a href="'+finalUrl+'" target="_blank"><img src="http://d3pim9r6015lw5.cloudfront.net/'+creativeUrl+'" width="'+str(width)+'" height="'+str(height)+'" border=0></a>')
  
	  if adIndex['b:'+str(args['bid'])+':type'] == 2:
	      self.write('<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" width="'+str(width)+'" height="'+str(height)+'"  id="mymoviename"><param name="movie" value="http://d3pim9r6015lw5.cloudfront.net/'+creativeUrl+'?clickTag='+urllib.quote(finalUrl)+'" /> <param name="quality" value="high" /> <param name="bgcolor" value="#ffffff" /><param name="wmode" value="transparent"><embed src="http://d3pim9r6015lw5.cloudfront.net/'+creativeUrl+'?clickTag='+urllib.quote(finalUrl)+'" quality="high" bgcolor="#ffffff" width="'+str(width)+'" height="'+str(height)+'" name="mymoviename" align="" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"> </embed> </object>')

	  if adIndex['b:'+str(args['bid'])+':type'] == 4:
	      code = adIndex['b:'+str(args['bid'])+':code']
	      code.replace("[CLICK_MACRO]",urllib.urlencode(finalUrl))
	      self.write(code)

	  if args.has_key('piggyback'):
	      pb=args['piggyback']
	      for p in pb:
		  self.write("<script src=\"http://rtbidder.impulse01.com/segment?group="+str(p)+"\"></script>")

	  #Set the view through cookie to indicate that this user has seen this ad impression.
	  #View through cookies are in the form of i203 where 203= campaign ID
	  cookiename = 'v'+str(args['cid'])        
	  impCookie = self.get_cookie(cookiename,default=False)
	  if impCookie == False:
	      impressionCount=0
	  else:
	      impCookie=json.loads(base64.b64decode(impCookie))
	      impressionCount = impCookie["impressionCount"]+1

	  cookieval = base64.b64encode(json.dumps({
	      "impressionId":impressionId,
	      "impressionCount":impressionCount,
	      "timestamp_GMT":datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S")
	  }))

	  if adIndex.has_key('vw:'+str(args['cid'])):
	      vw = adIndex['vw:'+str(args['cid'])]
	  else : 
	      vw=30
	  self.set_cookie(cookiename,cookieval,expires_days=vw)
	  self.flush()

	  message=json.dumps({"message":"IMP",
	      "impressionId":impressionId,
	      "imp_uid":imp_uid,
	      "campaignId":args['cid'],
	      "bannerId":args['bid'],
	      "exchange":args['e'],
	      "domain":args['d'],
	      "state":args['s'],
	      "city":args['c'],
	      "country":args["country"],
	      "bid":args['b'],
	      "price":encrPrice,
	      "impressionCount":impressionCount,
	      "isp":isp,
	      "ip":ip,
	      "timestamp_GMT":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	  })
	  self.sendToLogAgent(message)
	except:
	  print "exception : writing default ad to browser"
	  print sys.exc_info()
	  self.write("<a href=\"http://rtbidder.impulse01.com/click?id=84c380aa-67af-4f07-b044-8f549a35788f&cid=64&red=https://www.fundsindia.com/content/jsp/ELSSFunds.do?utm_source=impulse&utm_medium=display&utm_campaign=ELSS&utm_content=160X600\" target=\"_blank\"><img src=\"http://d3pim9r6015lw5.cloudfront.net/creatives/2/160x600_ELSS.gif\" width=\"160\" height=\"600\" border=0></a>")

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
