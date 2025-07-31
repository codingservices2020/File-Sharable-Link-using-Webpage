from flask import Flask
from threading import Thread
import requests
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Keep-alive server running"

def ping_self():
    while True:
        try:
            # requests.get("https://your-app-name.onrender.com")       # Ping your actual Render URL
            app.run(host='0.0.0.0', port=8080)
        except:
            pass
        time.sleep(300)  # Ping every 5 minutes

def keep_alive():
    t = Thread(target=ping_self)
    t.daemon = True
    t.start()

keep_alive()