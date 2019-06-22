import os
import time, wiringpi as pi
 
TRIG_PIN = 23
ECHO_PIN = 24
 
DURING = 5
CATCH_DISTANCE = 5
 
pi.wiringPiSetupGpio()
 
pi.pinMode( TRIG_PIN, pi.OUTPUT )
pi.pinMode( ECHO_PIN, pi.INPUT )
pi.digitalWrite( TRIG_PIN, pi.LOW )
time.sleep( 1 )
 
def mesure():
    pi.digitalWrite( TRIG_PIN, pi.HIGH )
    time.sleep(0.00001)
    pi.digitalWrite( TRIG_PIN, pi.LOW )
    while ( pi.digitalRead( ECHO_PIN ) == pi.LOW ):
        sigoff = time.time()
    while ( pi.digitalRead( ECHO_PIN ) == 1 ):
        sigon = time.time()
    return (( sigon - sigoff ) * 34000) / 2
 
count = 0
while True:
    distance = mesure()
    print ("Distance:", distance )
    if distance < CATCH_DISTANCE:
        count = count + 1
    else:
        count = 0
    if count == DURING:
        print ("Parkin in")
        os.system('/usr/bin/wget http://xxxx/parking.php?parking=in')
 
    time.sleep(1)