import utime
import json
import ujson
import reqs as requests

BASE_URL = "https://apptoogoodtogo.com/api/"
API_ITEM_ENDPOINT = "item/v7/"
LOGIN_ENDPOINT = "auth/v1/loginByEmail"
REFRESH_ENDPOINT = "auth/v1/token/refresh"
ALL_BUSINESS_ENDPOINT = "map/v1/listAllBusinessMap"
USER_AGENT = "TGTG/20.10.2 Stefan/2.1.0 (Linux; U; Android 6.0.1; Nexus 5 Build/M4B30"
DEFAULT_ACCESS_TOKEN_LIFETIME = 3600 * 4  # 4 hours

class TgtgClient:
	def __init__(
		self,
		url=BASE_URL,
		email=None,
		password=None,
		access_token=None,
		user_id=None,
		user_agent=None,
		language="en-UK",
		proxies=None,
		timeout=None,
		access_token_lifetime=DEFAULT_ACCESS_TOKEN_LIFETIME,
	):
		self.base_url = url

		self.email = email
		self.password = password

		self.access_token = access_token
		if self.access_token is not None:
			print("'access_token' is deprecated; use 'email' and 'password'")
		self.refresh_token = None
		self.last_time_token_refreshed = None
		self.access_token_lifetime = access_token_lifetime

		self.user_id = user_id
		if self.user_id is not None:
			print("'user_id' is deprecated; use 'email' and 'password'")
		self.user_agent = USER_AGENT
		self.language = language
		self.proxies = proxies
		self.timeout = timeout

	def _get_url(self, path):
		return self.base_url + path

	@property
	def _headers(self):
		headers = {"user-agent": self.user_agent, "accept-language": self.language}
		if self.access_token:
			headers["authorization"] = "Bearer " +self.access_token
		return headers


	def _refresh_token(self):
		"""refreshes access token via refresh endpoint"""
		last =  self.last_time_token_refreshed
		now =  utime.mktime(utime.localtime())
		if now-last <= self.access_token_lifetime*3600:
			return #no refresh needed when less then access_token_lifetime
		
		url = BASE_URL + REFRESH_ENDPOINT
		response = requests.post(url,headers=self._headers,json={"refresh_token": self.refresh_token})
		data = response.json()
		response.close()
		try:
			self.access_token = data["access_token"]
			self.refresh_token = data["refresh_token"]
			self.last_time_token_refreshed = utime.mktime(utime.localtime())
			self._saveData()
		except:
			raise Exception("Refresh Error")


	def _readData(self):
		"""reads session data from file"""
		f = open('config.json','r')
		data = json.load(f) 
		self.user_id = data["user_id"]
		self.access_token=data["access_token"]
		self.refresh_token=data["refresh_token"]
		self.last_time_token_refreshed = data["last_time_token_refreshed"]
		f.close()
		return data

	def _saveData(self):
		"""saves session data to file"""
		data = dict()
		data["user_id"] = self.user_id
		data["access_token"] = self.access_token
		data["refresh_token"] = self.refresh_token
		data["last_time_token_refreshed"] = self.last_time_token_refreshed
		
		# Serializing json  
		json_object = ujson.dumps(data)
		# Writing to sample.json 
		with open("config.json", "w") as outfile: 
			outfile.write(json_object)

	def _login(self):
		"""logs into tgtg account"""
		try:
			self._readData()
			self._refresh_token()
		except:
			print("new login")
			if not self.email or not self.password:
				raise ValueError(
					"You must fill email and password or access_token and user_id"
				)
			response = requests.post(self._get_url(LOGIN_ENDPOINT),headers=self._headers,json={"device_type": "IPHONE","email": self.email,"password": self.password})
			response = requests.post(self._get_url(LOGIN_ENDPOINT),headers=self._headers,json={"device_type": "IOS","email": self.email,"password": self.password})
			try:
				login_response = response.json()
				response.close()
				self.access_token = login_response["access_token"]
				self.refresh_token = login_response["refresh_token"]
				self.last_time_token_refreshed = utime.mktime(utime.localtime())
				self.user_id = login_response["startup_data"]["user"]["user_id"]
				self._saveData()

			except:
				raise Exception("Login Error")
			response.close()

#gets favorite items from tgtg api
	def get_items(
		self,
		*,
		latitude=0.0,
		longitude=0.0,
		radius=21,
		page_size=20,
		page=1,
		discover=False,
		favorites_only=True,
		item_categories=None,
		diet_categories=None,
		pickup_earliest=None,
		pickup_latest=None,
		search_phrase=None,
		with_stock_only=False,
		hidden_only=False,
		we_care_only=False,
	):
		self._login()

		# fields are sorted like in the app
		data = {
			"user_id": self.user_id,
			"origin": {"latitude": latitude, "longitude": longitude},
			"radius": radius,
			"page_size": page_size,
			"page": page,
			"discover": discover,
			"favorites_only": favorites_only,
			"item_categories": item_categories if item_categories else [],
			"diet_categories": diet_categories if diet_categories else [],
			"pickup_earliest": pickup_earliest,
			"pickup_latest": pickup_latest,
			"search_phrase": search_phrase if search_phrase else None,
			"with_stock_only": with_stock_only,
			"hidden_only": hidden_only,
			"we_care_only": we_care_only,
		}
		response = requests.post(self._get_url(API_ITEM_ENDPOINT),headers=self._headers,json=data)
		try:
			items = response.json()["items"]
			response.close()
			return items

		except:
			response.close()	
			raise Exception("API Error")
