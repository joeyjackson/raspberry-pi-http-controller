import time
import os
import logging
from threading import Thread, Lock

from sqlalchemy import Column, ForeignKey, Boolean, String, create_engine, select
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import RPi.GPIO as GPIO


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  LOGGER                                     #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

numeric_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO"), None)
if not isinstance(numeric_level, int):
  raise ValueError("Invalid log level: %s" % os.getenv("LOG_LEVEL", "INFO"))
# https://docs.python.org/3/library/logging.html#logrecord-attributes
# LOG_LEVEL: CRITICAL, ERROR, WARNING, INFO, or DEBUG
logging.basicConfig(
  level=numeric_level, 
  format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
)
logger = logging.getLogger("controller")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  DATABASE                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

Base = declarative_base()

class UserRole(Base):
  __tablename__ = "user_role"
  username = Column(ForeignKey("user.username"), primary_key=True)
  role_name = Column(ForeignKey("role.name"), primary_key=True)
  active = Column(Boolean)
  user = relationship("User", back_populates="roles")
  role = relationship("Role", back_populates="users")

class User(Base):
  __tablename__ = "user"
  
  username = Column(String, primary_key=True)
  password_hash = Column(String)
  
  roles = relationship("UserRole", back_populates="user")
  
  def __repr__(self):
    return f"User(username={self.username!r})"


class Role(Base):
  __tablename__ = "role"
  
  name = Column(String, primary_key=True)
  
  users = relationship("UserRole", back_populates="role")
  
  def __repr__(self):
    return f"Role(name={self.name!r})"

# Create admin user on first startup
db_filepath = os.getenv("DB_FILE_PATH", "db.sqlite")
engine = create_engine(f"sqlite:///{db_filepath}", future=True)
Session = sessionmaker(engine)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  AUTH                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

ADMIN_ROLE_NAME = "admin"

def setup_db():
  should_create_admin = not os.path.isfile(db_filepath)

  Base.metadata.create_all(engine)

  if should_create_admin:
    admin_username = os.getenv("ADMIN_USER", "admin")
    admin_pwd = os.getenv("ADMIN_PASSWORD")
    if not admin_pwd:
      raise Exception("Must specify ADMIN_PASSWORD")
    logger.info("Database not detected, creating with admin user (%s) at %s", admin_username, db_filepath)
    with Session() as session:
      admin_user = User(username=admin_username, password_hash=generate_password_hash(admin_pwd))
      admin_role = Role(name=ADMIN_ROLE_NAME)
      link = UserRole(active=True, role=admin_role, user=admin_user)
      session.add_all([admin_role, admin_user, link])
      session.commit()

# https://flask-httpauth.readthedocs.io/en/latest/
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
  with Session() as session:
    user = session.get(User, username)
    if user and check_password_hash(user.password_hash, password):
      return user.username

@auth.get_user_roles
def get_user_roles(user):
  with Session() as session:
    stmt = select(UserRole.role_name, UserRole.active).where(UserRole.username == user)
    roles = []
    for role, active in session.execute(stmt):
      if active:
        roles.append(role)
    return roles


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  GPIO / LEDs                                #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

LED_PIN = 40

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


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  ROUTES                                     #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

app = Flask(__name__)

@app.route("/")
@auth.login_required
def index():
  return render_template("index.html", current_user=auth.current_user())

@app.post("/api/led")
@auth.login_required(role=[ADMIN_ROLE_NAME])
def led_ctl():
  content_type = request.headers.get('Content-Type')
  if (content_type == 'application/json'):
    data = request.get_json()
    blink_count = data["blink_count"]
    blink_led_async(blink_count=blink_count)
    return "Blinking LED %s times" % blink_count
  else:
    return "Content-Type not supported!"


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  RUNNER                                     #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
  try:
    setup_db()
    setup_gpio()
    app.run(host="0.0.0.0")
  finally:
    cleanup_gpio()
  