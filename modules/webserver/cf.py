import os
import sys
import platform
import subprocess
import json
import time
import re
import threading
import urllib.request
import shutil

# Add parent directory to path to import config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Constants
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cf")
CLOUDFLARED_PATH = os.path.join(DATA_DIR, "cloudflared")
INFO_FILE = os.path.join(DATA_DIR, "info.json")
SERVER_PORT = 8000

def get_download_url():
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin": # macOS
        if machine == "arm64":
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64"
        else:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
    elif system == "linux":
        if machine == "aarch64" or machine == "arm64":
             return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        elif "arm" in machine:
             return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
        else:
             return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    elif system == "windows":
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

    raise Exception(f"Unsupported platform: {system} {machine}")

def check_cloudflared():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(CLOUDFLARED_PATH):
        print(f"Cloudflared not found at {CLOUDFLARED_PATH}. Downloading...")
        url = get_download_url()
        print(f"Downloading from {url}")

        try:
            with urllib.request.urlopen(url) as response, open(CLOUDFLARED_PATH, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            os.chmod(CLOUDFLARED_PATH, 0o755)
            print("Cloudflared downloaded and executable permissions set.")
        except Exception as e:
            print(f"Error downloading cloudflared: {e}")
            raise
    else:
        print("Cloudflared already exists.")

def start_tunnel():
    check_cloudflared()

    print(f"Starting Cloudflare Tunnel for port {SERVER_PORT}...")

    cmd = [CLOUDFLARED_PATH, "tunnel", "--url", f"http://localhost:{SERVER_PORT}"]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    url = None

    # Cloudflared outputs the URL to stderr usually
    # We need to read line by line but also not block forever if it fails

    start_time = time.time()
    while time.time() - start_time < 30: # 30 seconds timeout to find URL
        line = process.stderr.readline()
        if not line and process.poll() is not None:
            break

        if line:
            # print(f"CF Log: {line.strip()}")
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                url = match.group(0)
                print(f"Cloudflare Tunnel URL found: {url}")
                break

    if url:
        with open(INFO_FILE, 'w') as f:
            json.dump({"url": url}, f)

        # Keep reading stderr/stdout in separate threads to prevent buffer filling up
        def read_stream(stream):
            for _ in stream:
                pass
        threading.Thread(target=read_stream, args=(process.stderr,), daemon=True).start()
        threading.Thread(target=read_stream, args=(process.stdout,), daemon=True).start()

        return process
    else:
        print("Failed to find Cloudflare URL or timed out.")
        process.terminate()
        return None

if __name__ == "__main__":
    p = start_tunnel()
    if p:
        try:
            p.wait()
        except KeyboardInterrupt:
            p.terminate()
