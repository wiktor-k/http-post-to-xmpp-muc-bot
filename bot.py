import sys
import os

from twisted.internet import reactor
from twisted.names.srvconnect import SRVConnector
from twisted.words.protocols.jabber import client
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import xmlstream
from twisted.words.xish import domish
from twisted.web.server import Site #Web server for POST requests
from twisted.web.resource import Resource

class WebServer(Resource):
	def __init__(self, jabberClient):
		self.jabberClient = jabberClient

	def render_POST(self, request):
		"""Respond to a POST request"""
		print request.args["message"][0]
		self.jabberClient.sendMessage(request.content.read())
		return ''

class XMPPClientConnector(SRVConnector):
	def __init__(self, reactor, domain, factory):
		SRVConnector.__init__(self, reactor, 'xmpp-client', domain, factory)


	def pickServer(self):
		host, port = SRVConnector.pickServer(self)

		if not self.servers and not self.orderedServers:
			# no SRV record, fall back..
			port = 5222

		return host, port



class Client(object):
	def __init__(self, client_jid, secret, room, nickname):
		self.room = room
		self.nickname = nickname
		f = client.XMPPClientFactory(client_jid, secret)
		f.addBootstrap(xmlstream.STREAM_CONNECTED_EVENT, self.connected)
		f.addBootstrap(xmlstream.STREAM_END_EVENT, self.disconnected)
		f.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, self.authenticated)
		f.addBootstrap(xmlstream.INIT_FAILED_EVENT, self.init_failed)
		connector = XMPPClientConnector(reactor, client_jid.host, f)
		connector.connect()


	def rawDataIn(self, buf):
		print "RECV: %s" % unicode(buf, 'utf-8').encode('ascii', 'replace')


	def rawDataOut(self, buf):
		print "SEND: %s" % unicode(buf, 'utf-8').encode('ascii', 'replace')


	def connected(self, xs):
		print 'Connected.'

		self.xmlstream = xs

		# Log all traffic
		xs.rawDataInFn = self.rawDataIn
		xs.rawDataOutFn = self.rawDataOut

	def disconnected(self, xs):
		print 'Disconnected.'

		reactor.stop()


	def authenticated(self, xs):
		print "Authenticated."

		presence = domish.Element((None, 'presence'))
		xs.send(presence)
		xs.addObserver("/message", self.handleMessage)

		#reactor.callLater(5, xs.sendFooter)
		"""Join a MUC"""
		#We don't want to recieve any history upon entering the room
		history = domish.Element((None, 'history'))
		history['maxchars'] = '0'
		
		#We're using Multi-User Chat
		x = domish.Element((None, 'x'))
		x['xmlns'] = 'http://jabber.org/protocol/muc'
		presence = domish.Element((None, 'presence'))
		presence['to'] = self.room + '/' + self.nickname
		
		x.addChild(history)
		presence.addChild(x)
		print presence.toXml()
		xs.send(presence)

	def sendMessage(self, message):
		"""Send a message to the MUC"""
		m = domish.Element((None, 'message'))
		m['to'] = self.room
		m['type'] = 'groupchat'
		m.addElement('body', content = message)
		self.xmlstream.send(m)

	def init_failed(self, failure):
		print "Initialization failed."
		print failure

		self.xmlstream.sendFooter()

	def handleMessage(self, message):
		for el in message.elements():
			if el.name == "body":
				print("%s: %s" % (message["from"], el))

client_jid = jid.JID(os.environ['JID'])
secret = os.environ['PASSWORD']
c = Client(client_jid, secret, os.environ['ROOM'], os.environ['NICK'])

serverRoot = Resource()
serverRoot.putChild("robot", WebServer(c))
webFactory = Site(serverRoot)
reactor.listenTCP(80, webFactory)

reactor.run()