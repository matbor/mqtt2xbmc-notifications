#!/usr/bin/python
#
# XBMC MQTT Subscriber and custom popup
# october 2013 v1.0
#
# by Matthew Bordignon @bordignon
#
#  Format mqtt message using json 
#       {"lvl":"1","sub":"xxxxxx","txt":"xxxxxx","img":"xxx","del":"10000"}
#       {"lvl":"level either 1 or 2","sub":"subject text","txt":"main text 150 characters max","img":"icon location","del":"display msg this long"}
#
# todo;
# - need to change to a addon with config settings, currently just using the autoexec.py and modifying settings below
# - deal with the odd ascii characters, typical only has issues on the internal xbmc notification system
# - handle the exiting of XBMC, by killing this script nicely... will this effect will_set >? atm xbmc forces a kill
# - 

import mosquitto #you need to have this file
import xbmc
import json
import xbmcgui
import datetime
import socket

xbmc_name = socket.gethostname() #using the hostname for the mqtt will_set

#settings BEGIN
broker = "mqtt.localdomain" #mqtt broker location
broker_port = 1883 #mqtt broker port

topic_xbmcmsgs = "/house/xbmc/all/messages" 
topic_xbmcstatus = "/house/xbmc/"+xbmc_name+"/status" #the topic location for the mqtt online/offline last will and testament (will_set), using the xbmc hostname as well here

background = 'special://masterprofile/Thumbnails/background.png' #location of the background image for the popup box
mqtt_logo = 'special://masterprofile/Thumbnails/mqtt.png'
#settings END

print('XBMC MQTT -- Subscriber and custom popup starting on: ' + xbmc_name)

now = datetime.datetime.now()



class PopupWindow(xbmcgui.WindowDialog):
    def __init__(self, image, subject, text):
        #setup the text layout
        line1text = now.strftime("%d %B %Y at %I:%M%p")
        line2text = 'Message : ' + subject
        line3text = '-----------------------------'               
        line4text = text[:49]
        line5text = text[49:99]
        line6text = text[99:150]
        #define the XBMCgui control
        self.addControl(xbmcgui.ControlImage(10,10,700,180, background))
        self.addControl(xbmcgui.ControlImage(x=25, y=30, width=150, height=150, filename=image))
        self.addControl(xbmcgui.ControlLabel(x=190, y=25, width=900, height=25, label=line1text))
        self.addControl(xbmcgui.ControlLabel(x=190, y=50, width=900, height=25, label=line2text))
        self.addControl(xbmcgui.ControlLabel(x=190, y=75, width=900, height=25, label=line3text))
        self.addControl(xbmcgui.ControlLabel(x=190, y=100, width=900, height=25, label=line4text))
        self.addControl(xbmcgui.ControlLabel(x=190, y=125, width=900, height=25, label=line5text))
        self.addControl(xbmcgui.ControlLabel(x=190, y=150, width=900, height=25, label=line6text))

def on_connect(mosq, obj, rc):
    print("XBMC MQTT -- rc: "+str(rc))
    xbmc.executebuiltin('Notification(MQTT Connected,waiting for message,5000,'+mqtt_logo+')\'')
    mqttc.publish(topic_xbmcstatus, payload="online", qos=0, retain=True)
    

def on_message(mosq, obj, msg):
    print('XBMC MQTT -- message receieved')
    print("XBMC MQTT -- "+msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    #check to see if valid json string has been found, normally we just check the level.
    list = []
    try :
        list = json.loads(str(msg.payload))
        #if level-1 msg, use my popup window
        if list['lvl'] == "1":
            print("XBMC MQTT -- level 1 priority message")
            window = PopupWindow(list['img'],list['sub'],list['txt'])
            window.show()
            xbmc.sleep(int(list['del'])) #how long to show the window for
            window.close()
        #if level-2 msg, use xbmc builtin notification
        if list['lvl'] == "2":
            print("XBMC MQTT -- level 2 priority message")
            xbmc.executebuiltin('Notification('+list['sub']+','+list['txt']+','+list['del']+','+list['img']+')\'')
            
    except: #deal with the errors
        print('XBMC MQTT -- error, not sure why, sometimes it is because it might not valid JSON string revieved!')
        xbmc.executebuiltin('Notification(Error, not a valid message pls chk,10000,'+mqtt_logo+')\'')    

def on_publish(mosq, obj, mid):
    print("XBMC MQTT -- pulish mid: "+str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("XBMC MQTT -- Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mosq, obj, level, string):
    print("XBMC MQTT -- " + string)

# If you want to use a specific client id, use
# mqttc = mosquitto.Mosquitto("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.will_set(topic_xbmcstatus, payload="offline", qos=0, retain=True)
# Uncomment to enable debug messages
#mqttc.on_log = on_log
mqttc.connect(broker, broker_port, 60)
mqttc.subscribe(topic_xbmcmsgs, 0)

rc = 0
while rc == 0:
    rc = mqttc.loop()

print("XBMC MQTT -- rc: "+str(rc))
