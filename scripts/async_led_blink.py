import RPi.GPIO as GPIO
import time
from threading import Thread, Lock

def setup_gpio():
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(40, GPIO.OUT)

def cleanup_gpio():
  GPIO.cleanup()

gpio_lock = Lock()
def blink_led(blink_count):
  with gpio_lock:
    for _ in range(blink_count):
      GPIO.output(40,True)
      time.sleep(1)
      GPIO.output(40,False)
      time.sleep(1)

def blink_led_async(blink_count):
  Thread(target = blink_led, args = (blink_count,)).start()

if __name__ == "__main__":
  try:
    setup_gpio()
    blink_led_async(5)
    time.sleep(12)
  finally:
    cleanup_gpio()