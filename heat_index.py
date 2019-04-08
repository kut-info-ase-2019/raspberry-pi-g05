##########################################################################
# Filename    : dht11.py
# Description : test for SunFoudner DHT11 humiture & temperature module
# Author      : Alan
# Website     : www.osoyoo.com
# Update      : 2017/07/06
##########################################################################
import RPi.GPIO as GPIO
import time

#DHT11 connect to BCM_GPIO14
DHTPIN = 14
# set GPIO 0 as LED pin
LEDPINGREEN     = 5
LEDPINYELLOW    = 7
LEDPINRED       = 9

GPIO.setmode(GPIO.BCM)

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

#setup function for some setup---custom function
def setup():
    GPIO.setwarnings(False)
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    #set LEDPIN's mode to output,and initial level to LOW(0V)
    GPIO.setup(LEDPINGREEN,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(LEDPINYELLOW,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(LEDPINRED,GPIO.OUT,initial=GPIO.LOW)

def read_dht11_dat():
    GPIO.setup(DHTPIN, GPIO.OUT)
    GPIO.output(DHTPIN, GPIO.HIGH)
    time.sleep(0.05)
    GPIO.output(DHTPIN, GPIO.LOW)
    time.sleep(0.02)
    GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

    unchanged_count = 0
    last = -1
    data = []
    while True:
        current = GPIO.input(DHTPIN)
        data.append(current)
        if last != current:
            unchanged_count = 0
            last = current
        else:
            unchanged_count += 1
            if unchanged_count > MAX_UNCHANGE_COUNT:
                break

    state = STATE_INIT_PULL_DOWN

    lengths = []
    current_length = 0

    for current in data:
        current_length += 1

        if state == STATE_INIT_PULL_DOWN:
            if current == GPIO.LOW:
                state = STATE_INIT_PULL_UP
            else:
                continue
        if state == STATE_INIT_PULL_UP:
            if current == GPIO.HIGH:
                state = STATE_DATA_FIRST_PULL_DOWN
            else:
                continue
        if state == STATE_DATA_FIRST_PULL_DOWN:
            if current == GPIO.LOW:
                state = STATE_DATA_PULL_UP
            else:
                continue
        if state == STATE_DATA_PULL_UP:
            if current == GPIO.HIGH:
                current_length = 0
                state = STATE_DATA_PULL_DOWN
            else:
                continue
        if state == STATE_DATA_PULL_DOWN:
            if current == GPIO.LOW:
                lengths.append(current_length)
                state = STATE_DATA_PULL_UP
            else:
                continue
    if len(lengths) != 40:
        print "Data not good, skip"
        return False

    shortest_pull_up = min(lengths)
    longest_pull_up = max(lengths)
    halfway = (longest_pull_up + shortest_pull_up) / 2
    bits = []
    the_bytes = []
    byte = 0

    for length in lengths:
        bit = 0
        if length > halfway:
            bit = 1
        bits.append(bit)
    print "bits: %s, length: %d" % (bits, len(bits))
    for i in range(0, len(bits)):
        byte = byte << 1
        if (bits[i]):
            byte = byte | 1
        else:
            byte = byte | 0
        if ((i + 1) % 8 == 0):
            the_bytes.append(byte)
            byte = 0
    print the_bytes
    checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
    if the_bytes[4] != checksum:
        print "Data not good, skip"
        return False

    return the_bytes[0], the_bytes[2]

def main():
    print "Raspberry Pi wiringPi DHT11 Temperature test program\n"
    while True:
        result = read_dht11_dat()
        if result:
            humidity, temperature = result
            print "humidity: %s %%,  Temperature: %s C" % (humidity, temperature)
            heat_index = 0.81*temperature + 0.01*humidity*(0.99*temperature - 14.3) + 46.3 
            print "heat index: %s" % heat_index
            if heat_index < 75:
                GPIO.output(LEDPINGREEN,GPIO.HIGH)
                print('...LED ONn')
                time.sleep(0.5)

                GPIO.output(LEDPINGREEN,GPIO.LOW)
                print('LED OFF...n')
                time.sleep(0.5)
            elif heat_index < 80:
                GPIO.output(LEDPINYELLOW,GPIO.HIGH)
                print('...LED ONn')
                time.sleep(0.5)

                GPIO.output(LEDPINYELLOW,GPIO.LOW)
                print('LED OFF...n')
                time.sleep(0.5)
            else:
                GPIO.output(LEDPINRED,GPIO.HIGH)
                print('...LED ONn')
                time.sleep(0.5)

                GPIO.output(LEDPINRED,GPIO.LOW)
                print('LED OFF...n')
                time.sleep(0.5)

        time.sleep(1)



#define a destroy function for clean up everything after the script finished
def destroy():
    #turn off LED
    GPIO.output(LEDPIN,GPIO.LOW)
    #release resource
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        main()
    except KeyboardInterrupt:
        destroy() 
