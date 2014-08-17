try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

a = 0 

def my_callback(channel):
    a = 1
'''
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')
'''

def main():
    GPIO.setmode(GPIO.BOARD)

    print "Current Board Revision: ", GPIO.RPI_REVISION
    print "Current Board Version: ", GPIO.VERSION

    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(11, GPIO.BOTH)
    GPIO.add_event_callback(11, my_callback)

    if GPIO.input(11):
        print('Input was HIGH')
    else:
        print('Input was LOW')

    print "Initial state of pin 12 is: ", GPIO.input(12)

    GPIO.output(12, GPIO.HIGH)

    print "State at stage 1 of pin 12 is: ", GPIO.input(12)

    if GPIO.input(11):
        print('State at stage 1 is HIGH')
    else:
        print('State at stage 1 is LOW')

    GPIO.output(12, GPIO.LOW)

    print "State at stage 2 of pin 12 is: ", GPIO.input(12)

    GPIO.cleanup()
    
    print "a = ", a

#print "State after cleanup of pin 12 is: ", GPIO.input(12)

if __name__ == "__main__":
    main()