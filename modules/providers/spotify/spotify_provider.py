import os
import sys
import subprocess
import uuid
import glob

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import config

def check_spotdl_installed():
    try:
        process = subprocess.run(["spotdl", "--version"], capture_output=True, text=True)
        return process.returncode == 0
    except FileNotFoundError:
        return False

def download(url: str, options: dict = None):
    output_folder = os.path.abspath(config.output_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a temporary folder for this download to identify the file easily
    temp_id = str(uuid.uuid4())
    temp_dir = os.path.join(output_folder, temp_id)
    os.makedirs(temp_dir)

    try:
        # Use spotdl via subprocess
        # Assuming spotdl is in path or installed in env
        # Run in temp_dir to avoid path issues
        cmd = ["spotdl", url, "--output", "{artist} - {title}.{output-ext}"]

        process = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)

        if process.returncode != 0:
            return {
                "status": "error",
                "message": f"SpotDL failed: {process.stderr}"
            }

        # Find the downloaded file
        files = glob.glob(os.path.join(temp_dir, "*"))
        if not files:
             return {
                "status": "error",
                "message": "No file downloaded"
            }

        filepath = files[0]
        filename = os.path.basename(filepath)

        # Move file to main output folder
        final_path = os.path.join(output_folder, filename)
        os.rename(filepath, final_path)
        os.rmdir(temp_dir)

        return {
            "status": "success",
            "filepath": final_path,
            "filename": filename,
            "type": "audio"

        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
