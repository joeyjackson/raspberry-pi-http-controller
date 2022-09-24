import time
import os
import logging
from threading import Thread, Lock

from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import RPi.GPIO as GPIO

# LOG_LEVEL: CRITICAL, ERROR, WARNING, INFO, or DEBUG
numeric_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'), None)
if not isinstance(numeric_level, int):
  raise ValueError('Invalid log level: %s' % os.getenv('LOG_LEVEL', 'INFO'))
logging.basicConfig(level=numeric_level)

logger = logging.getLogger(__name__)

LED_PIN = 40

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
  logger.info("Setting up GPIO")
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(LED_PIN, GPIO.OUT)

def cleanup_gpio():
  logger.info("Cleaning up GPIO")
  GPIO.cleanup()

gpio_lock = Lock()
def blink_led(blink_count):
  with gpio_lock:
    logger.debug("Blinking LED %d times", blink_count)
    for _ in range(blink_count):
      GPIO.output(LED_PIN, True)
      time.sleep(1)
      GPIO.output(LED_PIN, False)
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
  return render_template('index.html', current_user=auth.current_user())

@app.post("/api/led")
@auth.login_required
def led_ctl():
  content_type = request.headers.get('Content-Type')
  if (content_type == 'application/json'):
    data = request.get_json()
    blink_count = data["blink_count"]
    blink_led_async(blink_count=blink_count)
    return "Blinking LED %s times" % blink_count
  else:
    return 'Content-Type not supported!'

if __name__ == "__main__":
  try:
    setup_gpio()
    app.run(host="0.0.0.0")
  finally:
    cleanup_gpio()
  