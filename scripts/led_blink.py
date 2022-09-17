import RPi.GPIO as GPIO
import time

if __name__ == "__main__":
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(40, GPIO.OUT)
  for _ in range(10):
    GPIO.output(40,True)
    time.sleep(1)
    GPIO.output(40,False)
    time.sleep(1)
  GPIO.cleanup()