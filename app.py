from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import RPi.GPIO as GPIO
import time
from threading import Thread, Lock

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
  "joey": generate_password_hash("secret_password")
}

def setup_gpio():
  print("Setting up GPIO")
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(40, GPIO.OUT)

def cleanup_gpio():
  print("Cleaning up GPIO")
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

@auth.verify_password
def verify_password(username, password):
  if username in users and check_password_hash(users.get(username), password):
    return username

@app.route("/")
@auth.login_required
def index():
  return "Hello, %s!" % auth.current_user()

@app.route("/api/led")
@auth.login_required
def led_ctl():
  blink_led_async(10)
  return "LED"

if __name__ == "__main__":
  try:
    setup_gpio()
    app.run(host="0.0.0.0")
  finally:
    cleanup_gpio()