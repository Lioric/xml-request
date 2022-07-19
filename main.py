import requests
import falcon
import os

from requests.structures import CaseInsensitiveDict
from wsgiref import simple_server

url = "http://186.42.112.70:8098/principal.asmx"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "text/xml; charset=utf-8"

data = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <SP_WS_FACTURAS_CLIENTE xmlns="http://tempuri.org/">
      <LN_CUE_ID>{}</LN_CUE_ID>
    </SP_WS_FACTURAS_CLIENTE>
  </soap:Body>
</soap:Envelope>
"""

API_FORWARDER_HOST = ""
# API_FORWARDER_HOST = "127.0.0.1"
API_FORWARDER_PORT = os.environ.get("PORT", 8888)
API_FORWARDER_RECEIVER = "http://xxxxxxxxxxxxxxxxxxxxxxxxxx"

class APIForwarderResource(object):

	def on_get(self, req, res, meterId):
		res.text = self.build_response(req, res, meterId)
		# res.body = self.build_response(req, res, action, False)

	# def on_post(self, req, res, action):
	# 	res.text = self.build_response(req, res, action)

	def build_response(self, req, res, meterId, isPost=True):
		xml = ""
		res.set_header("Content-type", "text/xml")
		res.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
		res.set_header("Access-Control-Allow-Origin", "*")
		res.status = falcon.HTTP_200

		if isPost:

			try:
				print("requesting", url)
				resp = requests.post(url, headers=headers, data=data.format(meterId))
				xml = resp.text
				print(resp.text)
				# print(resp.status_code)

				# json_post = json.load(req.stream)
				# py_request = requests.post("%s%s" % (API_FORWARDER_RECEIVER, action), json.dumps(json_post), headers={'content-type': 'application/json'})
				# ret = py_request.json()
			except Exception as e:
				print("The error is: %s" % str(e))
				res.status = falcon.HTTP_500
				ret = {}

		return xml

class APIForwarderServer(object):

	def __init__(self, host=API_FORWARDER_HOST, port=API_FORWARDER_PORT):
		self.host = host
		self.port = port
		self.falcon_app = falcon.API()
		self.forwarder_resource = APIForwarderResource()
		self.falcon_app.add_route("/mid/{meterId}", self.forwarder_resource)

	def runTestServer(self):

		test_server = simple_server.make_server(self.host, int(self.port),self.falcon_app)
		try:
			print("Running test server at: http://%s:%s" % (self.host, self.port))
			test_server.serve_forever()
		except KeyboardInterrupt:
			print("\nServer terminated...\n")

if __name__ == "__main__":

	forwarder_server = APIForwarderServer()
	forwarder_server.runTestServer()
