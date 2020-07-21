import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
Relay1_PIN = 14
Relay2_PIN = 15
GPIO.setup(Relay1_PIN, GPIO.OUT)
GPIO.setup(Relay2_PIN, GPIO.OUT)
print('[press ctrl+c to end the script]')
try: # Main program loop
  while True:
    GPIO.output(Relay1_PIN, GPIO.HIGH)
    GPIO.output(Relay2_PIN, GPIO.HIGH)
    print('Normally opened pin is HIGH')
    sleep(5) # Waitmode for 1 second
    GPIO.output(Relay1_PIN, GPIO.LOW)
    GPIO.output(Relay2_PIN, GPIO.LOW)
    print('Normally opened pin is LOW')
    sleep(5) # Waitmode for 1 second
# Scavenging work after the end of the program
except KeyboardInterrupt:
  print('Script end!')
finally:
  GPIO.cleanup()
