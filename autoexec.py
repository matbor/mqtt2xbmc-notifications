#!/usr/bin/python
#
# XBMC MQTT Subscriber and custom popup
# october 2013 v1.0
#
# by Matthew Bordignon @bordignon
#
#  Format mqtt message using json 
#       {"lvl":"1","sub":"xxxxxx","txt":"xxxxxx","img":"xxx","delay":"10000"}
#       {"lvl":"level either 1 or 2","sub":"subject text","txt":"main text 150 characters max","img":"icon location","delay":"display msg this long"}
#
# todo;
# - need to change to a addon with config settings, currently just using the autoexec.py and modifying settings below
# - deal with the odd ascii characters, typical only has issues on the internal xbmc notification system
# - handle the exiting of XBMC, by killing this script nicely... will this effect will_set >? atm xbmc forces a kill
# - make into a proper XBMC plugin, http://wiki.xbmc.org/index.php?title=How-to:Automatically_start_addons_using_services
# - publish to topic with status of playing/stopped/paused/resumed

import mosquitto #https://bitbucket.org/oojah/mosquitto/src/698853a74c8e/lib/python/mosquitto.py
import xbmc
import xbmcgui
import json
import datetime
import socket
import sys
import signal
import time


xbmc_name = socket.gethostname() #using the hostname for the mqtt will_set

#settings BEGIN
broker = "mqtt.localdomain" #mqtt broker location
broker_port = 1883 #mqtt broker port

topic_xbmcmsgs = "/house/xbmc/all/messages" 
topic_xbmcstatus = "/house/xbmc/"+xbmc_name+"/status" #the topic location for the mqtt online/offline last will and testament (will_set), using the xbmc hostname as well here
willtopic = "/house/xbmc/"+xbmc_name+"/status"
background = 'special://masterprofile/Thumbnails/background.png' #location of the background image for the popup box
mqtt_logo = 'special://masterprofile/Thumbnails/mqtt.png'
#settings END

print('XBMC MQTT -- Subscriber and custom popup starting on: ' + xbmc_name)

now = datetime.datetime.now()

mqttc = mosquitto.Mosquitto()

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

def cleanup(signum, frame):
    try:
        mqtt.publish(willtopic, "offline", retain=True)
        print("Disconnecting from broker")
        mqttc.disconnect()
    except:
        print("no broker?")
    print("Exiting on signal %d", signum)
    sys.exit(signum)        
        
def on_connect(mosq, obj, rc):
    print("XBMC MQTT -- rc: "+str(rc))
    xbmc.executebuiltin('Notification(MQTT Connected,waiting for message,10000,'+mqtt_logo+')\'')
    mqttc.publish(topic_xbmcstatus, payload="online", qos=0, retain=True)
    mqttc.subscribe(topic_xbmcmsgs, 0)

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
            xbmc.sleep(int(list['delay'])) #how long to show the window for
            window.close()
        #if level-2 msg, use xbmc builtin notification
        if list['lvl'] == "2":
            print("XBMC MQTT -- level 2 priority message")
            xbmc.executebuiltin('Notification('+list['sub']+','+list['txt']+','+list['delay']+','+list['img']+')\'')
            
    except: #deal with the errors
        print('XBMC MQTT -- error, not sure why, sometimes it is because it might not valid JSON string revieved!')
        xbmc.executebuiltin('Notification(Error, not a valid message pls chk,10000,'+mqtt_logo+')\'')    

def on_publish(mosq, obj, mid):
    print("XBMC MQTT -- pulish mid: "+str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("XBMC MQTT -- Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mosq, obj, level, string):
    print("XBMC MQTT -- " + string)

def main():
    """
    The main loop in which we stay connected to the broker
    """
    #define the callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    
    mqttc.will_set(willtopic, payload="offline", qos=0, retain=True)
    mqttc.reconnect_delay_set(delay=3, delay_max=30, exponential_backoff=True)
    
    try:
        mqttc.connect("mqtt.localdomain", 1883, 60)
    except Exception, e:
        print("XBMC MQTT -- MQTT connection failed: %s" % (str(e)))
        sys.exit(1)
    
    while True:
            try:
                mqttc.loop_forever()
            except socket.error:
                print("XBMC MQTT --MQTT server disconnected; sleeping")
                time.sleep(5)
                xbmc.executebuiltin('Notification(Error, mqtt disconnected pls chk,5000,'+mqtt_logo+')\'')    
            except:
                raise

    
if __name__ == '__main__':
    
    main()

