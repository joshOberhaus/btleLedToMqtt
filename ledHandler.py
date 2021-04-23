import paho.mqtt.client as mqtt
import os
from subprocess import Popen
import time
from bluepy import btle
#import daemon

address = "20:06:00:00:03:8C"
wrgbCharWrite = None
BLE_SERVICE_SET_WRGB = "0000ffd5-0000-1000-8000-00805f9b34fb"
BLE_CHARACTERISTIC_SET_WRGB = "0000ffd9-0000-1000-8000-00805f9b34fb"

effects = {
      'rainbow':           0x25, 
      'pulse_red':         0x26,
      'pulse_green':       0x27,  
      'pulse_blue':        0x28,  
      'pulse_yellow':      0x29,   
      'pulse_cyan':        0x2a, 
      'pulse_violet':      0x2b,   
      'pulse_white':       0x2c,  
      'pulse_red_green':   0x2d,      
      'pulse_red_blue':    0x2e,     
      'pulse_blue_green':  0x2f,       
      'rainbow_rave':      0x30   
}
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("lights/desk/rgb/cmd")
    client.subscribe("lights/desk/pwr/cmd")
    client.subscribe("lights/desk/effect/cmd")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if(msg.topic == "lights/desk/rgb/cmd"):
        rgb = list(map(int,msg.payload.decode('utf-8').split(',')))
        setRgb(rgb[0],rgb[1],rgb[2])
    elif(msg.topic == "lights/desk/pwr/cmd"):
        power('ON' in msg.payload.decode('utf-8'))
    elif(msg.topic == "lights/desk/effect/cmd"):
        setEffect(effects[msg.payload.decode('utf-8')])


def setEffect(effect, speed = 0x01):
    if (wrgbCharWrite):
        wrgbCharWrite.write(bytes([0xbb, effect, speed, 0x44]))

def setRgb(red, green, blue):
    if (wrgbCharWrite):
        wrgbCharWrite.write(bytes([0x56, red, green, blue, 0x00, 0xf0, 0xaa]))

def power(on):
    if (wrgbCharWrite):
        if(on):
            wrgbCharWrite.write(bytes([0xcc, 0x23, 0x33]))
        else:
            wrgbCharWrite.write(bytes([0xcc, 0x24, 0x33]))
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
    client.will_set("lights/desk/available",'offline',qos=1,retain=True)

    devLedBT = btle.Peripheral(address)
    wrgbSetUUID = btle.UUID(BLE_SERVICE_SET_WRGB)
    wrgbSetService = devLedBT.getServiceByUUID(wrgbSetUUID)

    uuidWrite  = btle.UUID(BLE_CHARACTERISTIC_SET_WRGB)
    wrgbCharWrite = wrgbSetService.getCharacteristics(uuidWrite)[0]

    client.connect("192.168.1.31", 1883, 60)
    client.publish("lights/desk/available",'online',qos=1,retain=True)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    run = True
    while run:
        time.sleep(0.1)
        client.loop_forever()
        
if __name__ == '__main__':
    main()