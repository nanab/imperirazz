#!/usr/bin/env python

import json
import web
import requests
import re
import base64
#Settings for razzberry connection
topLevelUrl = 'http://127.0.0.1:8083'
DevicesUrl= topLevelUrl +'/ZAutomation/api/v1/devices'
LocationsUrl= topLevelUrl +'/ZAutomation/api/v1/locations'
LoginUrl = topLevelUrl + '/ZAutomation/api/v1/login'


#Settings for imperirazz
authEnabled = 0 #change to 1 to enable authorization
usernameImperirazz = "username"
passwordImperirazz = "password"

#Start script
LoginHeader = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
Formlogin = '{"form": true, "login": "'+username+'", "password": "'+password+'", "keepme": false, "default_ui": 1}'

urls = (
	'/','index',
    '/devices(.*)', 'devices',
	'/system', 'system',
	'/rooms', 'rooms',
	'/login','login'
)

class devices:
	def GET(self, action):
		if authEnabled == 0 or web.ctx.env.get('HTTP_AUTHORIZATION') is not None:
			session = requests.Session()
			session.post(LoginUrl,headers=LoginHeader, data=Formlogin)
			if not action:
				response = session.get(DevicesUrl)
				gettedData = response.json()
				responseLocations = session.get(LocationsUrl)
				gettedDataLocations = responseLocations.json()
				output = []
				for data in gettedData['data']['devices']:
					typeData = ""
					idData = ""
					valueData = ""
					levelData = ""
					nameData = ""
					roomData = ""
					unitData = ""
					if data['permanently_hidden'] == 0:
						idData = data['id']
						nameData = data['metrics']['title']
						for data2 in gettedDataLocations['data']:
							try:
								for data3 in data2['namespaces']:
									if data3['id'] == "devices_all":
										for data4 in data3['params']:							
											if data4['deviceId'] == idData:
												roomData = data2['title']
												if roomData == "globalRoom":
													roomData = ""
							except:
								pass
						if data['deviceType'] == "switchMultilevel":
							typeData = "DevDimmer"
							levelData = data['metrics']['level']
							if levelData == 0:
								valueData = 0
							else:
								valueData = 1
							output.append({"id": idData, "name": nameData, "type": typeData, "room": roomData, "params": [{ "key": "Status", "value": valueData }, { "key": "Level", "value": levelData}]})

						if data['deviceType'] == "sensorMultilevel":
							probeTypeData = data['probeType']
							if not probeTypeData:
								probeTitle = data['metrics']['probeTitle']
								if probeTitle == "Distance":
									typeData = "DevGenericSensor"
									unitData = data['metrics']['scaleTitle']
							else:
								if probeTypeData == "temperature":
						 			typeData = "DevTemperature"
							if typeData:
								valueData = data['metrics']['level']
								output.append({"id": idData, "name": nameData, "type": typeData, "room": roomData, "params": [{ "key": "Value", "value": valueData, "unit": unitData, "graphable": "false" }]})
				finalSend = json.dumps(output)
				finalSend = finalSend[1:-1]
				finalSend = '{"devices": [' + finalSend + ']}'
				return finalSend
			else:
				print action
				actionSplitted = action.split('/')
				devAction = actionSplitted[2]
				if devAction == "action":
					devId = actionSplitted[1]			
					devActionName = actionSplitted[3]
					devActionParam = actionSplitted[4]
					if devActionName == "setStatus": #param = 0 or 1
						if devActionParam == "1":
							response = session.get(topLevelUrl + "/ZAutomation/api/v1/devices/" + devId + "/command/on")
							gettedData = response.json()
							if gettedData['code'] == 200:
								return json.dumps({"success": "true"})
						elif devActionParam == "0":
							response = session.get(topLevelUrl + "/ZAutomation/api/v1/devices/" + devId + "/command/off")
							gettedData = response.json()
							if gettedData['code'] == 200:
								return json.dumps({"success": "true"})
						else:
							pass
					elif devActionName == "setLevel": #param = 0 - 100 
						response = session.get(topLevelUrl + "/ZAutomation/api/v1/devices/" + devId + "/command/exact?level=" + devActionParam)
						gettedData = response.json()
						if gettedData['code'] == 200:
							return json.dumps({"success": "true"})
					else:
						pass
		else:
			raise web.seeother('/login')

class system:
	def GET(self):
		if authEnabled == 0 or web.ctx.env.get('HTTP_AUTHORIZATION') is not None:
			return json.dumps({"id": "imperirazz", "apiversion": 1})
		else:
			raise web.seeother('/login')

class rooms:
	def GET(self):
		if authEnabled == 0 or web.ctx.env.get('HTTP_AUTHORIZATION') is not None:
			roomData = ""
			output = []
			session = requests.Session()
			session.post(LoginUrl,headers=LoginHeader, data=Formlogin)
			responseLocations = session.get(LocationsUrl)
			gettedDataLocations = responseLocations.json()
			for data2 in gettedDataLocations['data']:
				roomData = data2['title']
				if roomData == "globalRoom":
					pass
				else:
					output.append({"id": roomData, "name": roomData})
			finalSend = json.dumps(output)
			finalSend = finalSend[1:-1]
			finalSend = '{"rooms": [' + finalSend + ']}'
			return finalSend
		else:
			raise web.seeother('/login')

class login:
    def GET(self):
		auth = web.ctx.env.get('HTTP_AUTHORIZATION')
		authreq = False
		if auth is None:
			authreq = True
		else:
			auth = re.sub('^Basic ','',auth)
			username,password = base64.decodestring(auth).split(':')
			if (username == usernameImperirazz) and (password == passwordImperirazz):
				raise web.seeother('/')
			else:
				authreq = True
		if authreq:
			web.header('WWW-Authenticate','Basic realm="Auth example"')
			web.ctx.status = '401 Unauthorized'
			return
class index:
	def GET(self):
		if authEnabled == 0 or web.ctx.env.get('HTTP_AUTHORIZATION') is not None:
			return 'Imperirazz ISS for Imperihome'
		else:
			raise web.seeother('/login')

def common_headers():
    web.header('Content-type', "application/json")
    web.header('Access-Control-Allow-Origin', "*")

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(common_headers))
    app.run()


