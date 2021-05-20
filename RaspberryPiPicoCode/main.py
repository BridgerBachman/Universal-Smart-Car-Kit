"""
__author__ = "Bridger Miles, Chance Cochrane"
__license__ = "GNU General Public License, version 2"
__version__ = "Beta"
__email__ = "10766744@uvu.edu, 10816910@uvu.edu"
__status__ = "Final BSM MCU Code"
"""
#This is the main program that is ran on the microcontroller to send data to the Raspberry Pi about the status of each blindspot.
#Importing the MicroPython Libraries for Pin and utime.
from machine import Pin
import utime

#Initizlizing the trigger and echo pins for both ultrasonic sensors.
trigger = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN)
trigger2 = Pin(17, Pin.OUT)
echo2 = Pin(16, Pin.IN)

#Initializing the onboard led for debugging.
led = Pin(25, Pin.OUT)

#Initizliaing the 2 transmission lines to emit the boolean signals
#to the raspberry pi for left and right side of car.
rightled = Pin(14, Pin.OUT)
leftled = Pin(11, Pin.OUT)


def sensor():
    trigger.low()#Set the trigger to low
    utime.sleep_us(1)#wait 1 micro seconds for floating voltage to dissapear
    trigger.high()#set the trigger pin to high
    utime.sleep_us(5)#wait 5 microseconds
    trigger.low()#back to low for next cycle added as protection
    
    while echo.value() == 0:#While echo is nonexistent
        noSignal = utime.ticks_us()#tick the clock 1us at a time
    while echo.value() == 1: #While echo is being recieved
        signalRecieved = utime.ticks_us()#tick the clock 1us at a time
    time = signalRecieved - noSignal

    #Distance (Feet converted later) = Speed (1125 Foot/per second) * Time in us 
    distance = (time * 1125) / 2 # /2 since the signal is sent then recieved.
    return distance


# Had to duplicate above algorithm so they can be ran in series without overlaping values for different sensors.
def sensor2():#Same algorithm as above 
    trigger2.low()
    utime.sleep_us(1)
    trigger2.high()
    utime.sleep_us(5)
    trigger2.low()
    
    while echo2.value() == 0:
        noSignal2 = utime.ticks_us()
    while echo2.value() == 1:
        signalRecieved2 = utime.ticks_us()
    time2 = signalRecieved2 - noSignal2
    
    distance2 = (time2 * 1125) / 2
    return distance2


try:
    while 1:#Starting point of code.
        #Query both results one after another from the sensors
        result = sensor()
        result2 = sensor2()

        #if  right object is less than 6 feet emit light, else do nothing
        if (result/1000000) < 6:
            #print('right detected')#debug use only
            led.toggle()#blinks onboard led to ensure program is running.
            rightled.high()#Send signal to pi
        else:
            rightled.low()#dont send signal to pi
        #if  left object is less than 6 feet emit light, else do nothing
        if (result2/1000000) < 6:
            #print('left detected')#debug use only
            led.toggle()#blinks onboard led to ensure program is running.
            leftled.high()
        else:
            leftled.low()
        #print('Sensor 1: ',result/1000000, 'feet')#debug outputs precise distance.
        #print('Sensor 2: ',result2/1000000, 'feet')
        utime.sleep(0.25)  #do this task 4 times a second. turn up for more accuracy.          
except KeyboardInterrupt: #Detects unexpected termination program will automatically restart CTRL^C
    pass#Do nothing when keyboard exception is caught. restart is taken care of by the pico firmware.

