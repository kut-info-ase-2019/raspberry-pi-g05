import RPi.GPIO as GPIO
import time
import os
import pexpect # to automatically input password for scp
import getpass
from multiprocessing import Pool

# set BCM_GPIO 17(wPi#0) as PIR pin
PIRPin = 17
# 使用するGPIO
GPIO_PIN = 18

def setup():
    GPIO.setwarnings(False)
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    #set BuzzerPin's mode to output,and initial level to HIGH(3.3V)
    #GPIO.setup(BuzzerPin,GPIO.OUT,initial=GPIO.HIGH)
    GPIO.setup(PIRPinIn,GPIO.IN)
    GPIO.setup(PIRPinOut,GPIO.IN)

def main():

    while True:
        #read Sw520dPin's level
        if(GPIO.input(PIRPinIn)!=0):
            starttime=time.time()
            runtime = 0
            print ('********************')
            print ('*     In Sensor!     *')
            print ('********************')
            print ('\n')
            while(runtime < 3):
                runtime = time.time() - starttime
                if(GPIO.input(PIRPinOut)!=0):
                    print("=============")
                    print("    Out    ")
                    print("=============")
                    time.sleep(5)
                    setup()
                    break
            time.sleep(1)

        elif(GPIO.input(PIRPinOut)!=0):
            starttime=time.time()
            runtime = 0
            print ('*******************')
            print ('*    Out Sensor    *')
            print ('*******************')
            print('\n')
            while(runtime < 3):
                runtime = time.time() - starttime
                if(GPIO.input(PIRPinIn)!=0):
                    print("===============")
                    print("     In      ")
                    print("===============")
                    time.sleep(5)
                    break
            time.sleep(1)
        else:
            #print ('====================')
            print ('=     Not alarm...  =')
            #print ('====================')
            print ('\n')
        time.sleep(1)

if __name__ == '__main__':
    setup() # 色々初期化
    try:
            main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        destroy()
        pass