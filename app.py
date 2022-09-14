from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
  "joey": generate_password_hash("pwd")
}

@auth.verify_password
def verify_password(username, password):
  if username in users and check_password_hash(users.get(username), password):
      return username

@app.route('/')
@auth.login_required
def index():
  return "Hello, %s!" % auth.current_user()

@app.post('/api/led')
@auth.login_required
def led_ctl():

  return "LED"

if __name__ == '__main__':
  app.run()