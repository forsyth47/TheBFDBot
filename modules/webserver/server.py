import os
import sys
from flask import Flask, send_from_directory # type: ignore

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

app = Flask(__name__)
PORT = 8000

# Ensure the output folder exists
if not os.path.exists(config.output_folder):
    os.makedirs(config.output_folder)

@app.route('/<path:filename>')
def serve_file(filename):
    # Use os.path.abspath to ensure we are serving from the correct absolute path
    directory = os.path.abspath(config.output_folder)
    return send_from_directory(directory, filename)

def run_server():
    # Run threaded=True to handle multiple requests if needed, though for this use case simple is fine
    app.run(host='0.0.0.0', port=PORT, threaded=True)

if __name__ == "__main__":
    run_server()
