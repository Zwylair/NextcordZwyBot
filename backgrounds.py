from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
  return ':D'


def start_keeping():
  thread = Thread(target=lambda: app.run(host='0.0.0.0', port=80))
  thread.start()
