#!/usr/bin/python
"""
This file is part of the web2py Web Framework
Copyrighted by Massimo Di Pierro <mdipierro@cs.depaul.edu>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

1) install tornado

   easy_install tornado

2) start this app:

   python gluon/contrib/comet_messaging.py -k mykey -p 8888

3) from any web2py app you can post messages with

   from gluon.contrib.comet_messaging import comet_send
   comet_send('http://127.0.0.1:8888','Hello World','mykey','mygroup')

4) from any template you can receive them with

   <script>
   $(document).ready(function(){
      if(!web2py_comet('ws://127.0.0.1:8888/realtime/mygroup',function(e){alert(e.data)}))
         alert("html5 websocket not supported by your browser, try Google Chrome");
   });
   </script>

When the server posts a message, all clients connected to the page will popup an alert message
Or if you want to send json messages and store evaluated json in a var called data:

   <script>
   $(document).ready(function(){
      var data;
      web2py_comet('ws://127.0.0.1:8888/realtime/mygroup',function(e){data=eval('('+e.data+')')});
   });
   </script>

- All communications between web2py and comet_messaging will be digitally signed with hmac.
- All validation is handled on the web2py side and there is no need to modify comet_messaging.py
- Multiple web2py instances can talk with one or more comet_messaging servers.
- "ws://127.0.0.1:8888/realtime/" must be contain the IP of the comet_messaging server.
- Via group='mygroup' name you can support multiple groups of clients (think of many chat-rooms)

Here is a complete sample web2py action:

    def index():
        form=LOAD('default','ajax_form',ajax=True)
        script=SCRIPT('''
            jQuery(document).ready(function(){
              var callback=function(e){alert(e.data)};
              if(!web2py_comet('ws://127.0.0.1:8888/realtime/mygroup',callback))
                alert("html5 websocket not supported by your browser, try Google Chrome");
            });
        ''')
        return dict(form=form, script=script)

    def ajax_form():
        form=SQLFORM.factory(Field('message'))
        if form.accepts(request,session):
            from gluon.contrib.comet_messaging import comet_send
            comet_send('http://127.0.0.1:8888',form.vars.message,'mykey','mygroup')
        return form

Acknowledgements:
Tornado code inspired by http://thomas.pelletier.im/2010/08/websocket-tornado-redis/

"""

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import hmac
import sys
import optparse
import urllib
import time

listeners = {}

def comet_send(url,message,hmac_key=None,group='default'):
    sig = hmac_key and hmac.new(hmac_key,message).hexdigest() or ''
    params = urllib.urlencode({'message': message, 'signature': sig, 'group':group})
    f = urllib.urlopen(url, params)
    data= f.read()
    f.close()
    return data

class PostHandler(tornado.web.RequestHandler):
    def post(self):
        if hmac_key and not 'signature' in self.request.arguments: return 'false'
        if 'message' in self.request.arguments:
            message = self.request.arguments['message'][0]
            group = self.request.arguments.get('group',['default'])[0]
            print '%s:MESSAGE to %s:%s' % (time.time(), group, message)
            if hmac_key:
                signature = self.request.arguments['signature'][0]
                if not hmac.new(hmac_key,message).hexdigest()==signature: return 'false'
            for client in listeners.get(group,[]): client.write_message(message)
            return 'true'
        return 'false'

class DistributeHandler(tornado.websocket.WebSocketHandler):
    def open(self,group=None):
        self.group = group or 'default'
        if not self.group in listeners: listeners[self.group]=[]
        listeners[self.group].append(self)
        print '%s:CONNECT to %s' % (time.time(), self.group)
    def on_message(self, message):
        pass
    def on_close(self):
        if self.group in listeners: listeners[self.group].remove(self)
        print '%s:DISCONNECT from %s' % (time.time(), self.group)

if __name__ == "__main__":
    usage = __doc__
    version= ""
    parser = optparse.OptionParser(usage, None, optparse.Option, version)
    parser.add_option('-p',
                      '--port',
                      default='8888',
                      dest='port',
                      help='socket')
    parser.add_option('-k',
                      '--hmac_key',
                      default='',
                      dest='hmac_key',
                      help='hmac_key')
    (options, args) = parser.parse_args()
    hmac_key = options.hmac_key
    urls=[
        (r'/', PostHandler),
        (r'/realtime/(\w*)', DistributeHandler)]
    application = tornado.web.Application(urls, auto_reload=True)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(int(options.port))
    tornado.ioloop.IOLoop.instance().start()
