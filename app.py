import time
import os
from threading import Thread, Lock

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import RPi.GPIO as GPIO


app = Flask(__name__)
auth = HTTPBasicAuth()

admin_username = os.getenv('ADMIN_USER', 'admin')
admin_pwd = os.getenv('ADMIN_PASSWORD')
if not admin_pwd:
  raise Exception("Must specify ADMIN_PASSWORD")

users = {
  admin_username: generate_password_hash(admin_pwd)
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
  return "Raspberry Pi Controller - current user: %s" % auth.current_user()

@app.route("/api/led")
@auth.login_required
def led_ctl():
  blink_led_async(5)
  return "LED"

if __name__ == "__main__":
  try:
    setup_gpio()
    app.run(host="0.0.0.0")
  finally:
    cleanup_gpio()