# bot/alive.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Bot is Alive!</h1><p>System Status: OK</p>"

if __name__ == "__main__":
    from config import Config
    app.run(host='0.0.0.0', port=Config.PORT, debug=False)
