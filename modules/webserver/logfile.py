# Web server to serve the log files

import os
import sys
from flask import Flask, send_from_directory  # type: ignore
from threading import Thread

# Disable the Flask development server banner
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# Run on port 8080 or keep +1 until an unused port is found
PORT = 8080
while True:
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", PORT))
        break
    except OSError:
        PORT += 1

app = Flask(__name__)
# Ensure the log folder exists
@app.route('/')
# serve the contents of the whole data folder and its files (not one specific file)
def serve_file(filename='log.txt'):
    # Use os.path.abspath to ensure we are serving from the correct absolute path
    directory = os.path.abspath('./data/logs')
    return send_from_directory(directory, filename)

def run_server():
    # Run threaded=True to handle multiple requests if needed, though for this use case simple is fine
    print(f"Starting log file web server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True)

def serve_logs_via_web_server():
    t = Thread(target=run_server, daemon=True)
    t.start()

if __name__ == "__main__":
    run_server()
