import paho.mqtt.client as mqtt
import os
from subprocess import Popen
import time
from bluepy import btle
import bluepy
#import daemon

address = "78:9C:70:01:55:99"
wrgbCharWrite = None
BLE_SERVICE_SET_WRGB = "0000ffe0-0000-1000-8000-00805f9b34fb"
BLE_CHARACTERISTIC_SET_WRGB = "0000ffe1-0000-1000-8000-00805f9b34fb"
# :9C:70:01:55:99][LE]> char-write-cmd f 7eff0503d7ff66ffef
# [78:9C:70:01:55:99][LE]> char-write-cmd f 7eff0503d7ff00ffef
# [78:9C:70:01:55:99][LE]> char-write-cmd f 7eff0503d7ffffffef

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("lights/jessdesk/rgb/cmd")
    client.subscribe("lights/jessdesk/pwr/cmd")
    client.subscribe("lights/jessdesk/effect/cmd")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if(msg.topic == "lights/jessdesk/rgb/cmd"):
        rgb = list(map(int,msg.payload.decode('utf-8').split(',')))
        setRgb(rgb[0],rgb[1],rgb[2])
    elif(msg.topic == "lights/jessdesk/pwr/cmd"):
        power('ON' in msg.payload.decode('utf-8'))
    elif(msg.topic == "lights/jessdesk/effect/cmd"):
        setEffect(effects[msg.payload.decode('utf-8')])


def setEffect(effect, speed = 0x01):
    if (wrgbCharWrite):
        wrgbCharWrite.write(bytes([0xbb, effect, speed, 0x44]))

def setRgb(red, green, blue):
    if (wrgbCharWrite):
        wrgbCharWrite.write(bytes([0x7e, 0xff, 0x05, 0x03, red, green, blue,0xff, 0xef]))

def power(on):
    if (wrgbCharWrite):
        if(on):
            wrgbCharWrite.write(bytes([0x7e,0xff,0x04,0x01,0xff,0xff,0xff,0xff,0xef]))
        else:
            wrgbCharWrite.write(bytes([0x7e,0xff,0x04,0x00,0xff,0xff,0xff,0xff,0xef]))
#rainbow: bb250144
# flash red: bb260144
#greeb, b, y, cya, vio, white

#red/green: bb2d0144
# red blue
# green blue

#rainbow rave



def main():
    global wrgbCharWrite
    p = None
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.will_set("lights/jessdesk/available",'offline',qos=1,retain=True)

    client.connect("192.168.1.31", 1883, 60)
    client.publish("lights/jessdesk/available",'online',qos=1,retain=True)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.

    deviceConnected = False
    run = True
    while run:
        time.sleep(0.1)
        if(not deviceConnected):
            client.publish("lights/jessdesk/available",'offline',qos=1,retain=True)
            print("Attempting to connect...")
            try:
                print("what")
                devLedBT = btle.Peripheral(address)
                print("is")
                wrgbSetUUID = btle.UUID(BLE_SERVICE_SET_WRGB)
                print("really")
                wrgbSetService = devLedBT.getServiceByUUID(wrgbSetUUID)
                print("going")
                uuidWrite  = btle.UUID(BLE_CHARACTERISTIC_SET_WRGB)
                print("on")
                wrgbCharWrite = wrgbSetService.getCharacteristics(uuidWrite)[0]
                print("here")
                client.publish("lights/jessdesk/available",'online',qos=1,retain=True)
                print("now")
                deviceConnected = True
            except bluepy.btle.BTLEDisconnectError:
                print("Couldn't connect, waiting a second")
                time.sleep(1)
        if(wrgbCharWrite and deviceConnected):
            try:
                client.loop(timeout=1.0, max_packets=1)
            except bluepy.btle.BTLEDisconnectError:
                deviceConnected = False

if __name__ == '__main__':
    main()