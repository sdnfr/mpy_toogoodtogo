import network
import utime
import reqs as requests
import ujson
from tgtg import TgtgClient
import config 

#flashing micropython: 
# esptool.py --chip esp32 --port COM3 erase_flash
# esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-idf3-20200902-v1.13.bin
#copying files via ampy:
# ampy --port COM3 put boot.py
# ampy --port COM3 put config.py
# ampy --port COM3 put reqs.py
# ampy --port COM3 put tgtg.py

NOTIFICATION_REFRESH = 10 * 60 #10 minutes: time in seconds that a new message might be send
wlan = None

def initWlan():
	"""initializes and connects WLAN"""
	global wlan
	wlan = network.WLAN(network.STA_IF) # create station interface
	wlan.active(True)	   # activate the interface
	try :
		wlan.connect(config.essid, config.pw) #connect to network
	except:
		print("could not connect to wlan")
	utime.sleep_ms(5000)


def getMessages():
	"""Gets messages from telegram chat"""
	answer = requests.get("https://api.telegram.org/bot" + token + "/getUpdates")
	content = answer.content
	answer.close()
	data = json.loads(content)
	print(data)

def sendMessage(message):
	"""sends message to telegram chat with chat_id set in config.py"""
	global chat_id
	params = {"chat_id": chat_id, "text":message}
	url = "https://api.telegram.org/bot" + token + "/sendMessage"
	answer = requests.post(url, json=params)
	answer.close()

def update():
	"""fetches items from tgtg API and sends telegram notification"""
	global postedItems
	items = tg.get_items() #fetches items from api
	for item in items:
		id = item['item']['item_id']
		name = item['item']['name']
		store = item['store']['store_name']
		branch = item['store']['branch']
		if item['items_available'] > 0:
			if not id in postedItems: #only sends message if not posted before
				sendMessage(getMessageText(store,branch,name))
				postedItems.append(id)
		else:
			if id in postedItems: #removes item if sold out again
				postedItems.remove(id)

def getMessageText(store,branch,name):
	"converts input into readable message text"
	if name == "":
		name = "etwas"
	return "Wuhu! Bei %s - %s gibt es %s!"%(store, branch,name)


postedItems = []
token = None
chat_id = None
try:
	import config
	token = config.telegram_token
	chat_id = config.telegram_chat_id
	tg = TgtgClient(email= config.tgtg_email,password= config.tgtg_pw)
except:
	print("could not set up TGTG")

initWlan()
print("wlan initialized")

while True:
	update()
	utime.sleep_ms(10000)

