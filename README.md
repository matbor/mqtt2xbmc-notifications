XBMC-MQTT-notification-system
=============================

Subscribes to a MQTT topic and will display the messages on XBMC using custom popup or the built in XBMC notification system, if the message is formated correctly.

Typical format of the MQTT message that needs to be sent to topic.

    {"lvl":"1","sub":"xxxxxx","txt":"xxxxxx","img":"xxx","del":"10000"}

    lvl -- Message level; a  "1"  uses the custom larger popup, a "2"  uses the xbmc built in notification. (see screenshots below)
    sub -- subject of message
    txt -- main body of text, needs to be less than 150 characters for the custom larger popup
    img -- ?? pixels, transparent background, location and name, eg. special://masterprofile/Thumbnails/xxx_1.png
    del -- show message for this long, in miliseconds

##Installation;
- copy autoexec.py & mosquitto.py to XBMC userdate folder.
- copy background.png and mqtt.png to a folder
- edit autoexec.py and change the broker and topic settings.

##Notes;
- Using autoexec.py as I haven't got around to making it a plugin yet... it's on the todo list!
- to get the latest version of mosquitto.py please visit http://www.mosquitto.com <- doubt latest version will work
- have tested on ATV2 with XBMC frodo 12.2 and Windows7 with XBMC frodo 12.2 succesfully.

##Example:
###Startup

This shows that it has connected successfully to the broker.

![Startup](https://raw.github.com/matbor/XBMC-MQTT-notification-system/master/screenshots/startup.png)

###Level-1 Message

Custom pop-up

JSON string sent to topic;

    {"lvl":"1","sub":"@CFA_Updates","txt":"Visiting NSW's tomorrow? Monitor fire conditions. Follow @nswrfs and remember many parks & reserves closed http://www.environment.nsw.gov.au/NationalParks/FireClosure.aspx #nswfires","img":"special://masterprofile/Thumbnails/cfa.png","del":"20000"}

![level1msg](https://raw.github.com/matbor/XBMC-MQTT-notification-system/master/screenshots/level1msg.png)

###Level-2 Message

Using bulit-in XBMC notification system

JSON string sent to topic;

    {"lvl":"2","sub":"@CFA_Updates","txt":"Visiting NSW's tomorrow? Monitor fire conditions. Follow @nswrfs and remember many parks & reserves closed http://www.environment.nsw.gov.au/NationalParks/FireClosure.aspx #nswfires","img":"special://masterprofile/Thumbnails/cfa.png","del":"20000"}


![level2msg](https://raw.github.com/matbor/XBMC-MQTT-notification-system/master/screenshots/level2msg.png)

##todo;
- need to change to a xbmc addon with config settings, currently just using the autoexec.py and modifying settings in script.
- deal with the odd ascii characters, typical only has issues on the internal xbmc notification system
- handle the exiting of XBMC, by killing this script nicely... will this effect will_set >? atm xbmc forces a kill
- add back in reporting of playback status, play/stop/pause/resume/now playing
- fix so it works with latest version of mosquitto.py
