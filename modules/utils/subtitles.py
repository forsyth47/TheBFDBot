import os
import asyncio
import requests
import shutil
import uuid

def download_subtitle(url, path):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Failed to download subtitle {url}: {e}")
        return False

async def embed_subtitles(video_path, subtitles_data):
    """
    Downloads and embeds subtitles into the video file.
    subtitles_data: list of {'url': str, 'lang': str}
    """
    if not subtitles_data or not os.path.exists(video_path):
        return video_path

    print(f"Embedding {len(subtitles_data)} subtitles into {video_path}")

    temp_dir = os.path.join(os.path.dirname(video_path), f"subs_{uuid.uuid4()}")
    os.makedirs(temp_dir, exist_ok=True)

    downloaded_subs = []

    # Download subtitles in parallel using threads
    loop = asyncio.get_running_loop()
    tasks = []

    for i, sub in enumerate(subtitles_data):
        url = sub.get('url')
        if not url: continue

        ext = url.split('.')[-1].split('?')[0]
        if len(ext) > 4 or '/' in ext:
            ext = 'vtt' # Default to vtt

        filename = f"sub_{i}.{ext}"
        filepath = os.path.join(temp_dir, filename)
        lang = sub.get('lang', 'und')

        tasks.append(loop.run_in_executor(None, download_subtitle, url, filepath))
        downloaded_subs.append({'path': filepath, 'lang': lang})

    results = await asyncio.gather(*tasks)

    # Filter out failed downloads
    valid_subs = [sub for sub, success in zip(downloaded_subs, results) if success]

    if not valid_subs:
        shutil.rmtree(temp_dir)
        return video_path

    # Construct ffmpeg command
    # We output to a temp file then rename
    output_path = f"{video_path}_embed.mp4"

    cmd = ['ffmpeg', '-y', '-i', video_path]

    # Add subtitle inputs
    for sub in valid_subs:
        cmd.extend(['-i', sub['path']])

    # Map streams
    cmd.extend(['-map', '0']) # Map all streams from video

    for i in range(len(valid_subs)):
        cmd.extend(['-map', f'{i+1}']) # Map each subtitle stream

    # Copy video and audio
    cmd.extend(['-c:v', 'copy', '-c:a', 'copy'])

    # Set subtitle codec and metadata
    # For MP4, mov_text is standard.
    cmd.extend(['-c:s', 'mov_text'])

    for i, sub in enumerate(valid_subs):
        # Try to generate a 3-letter code from the language name
        lang_code = sub['lang'][:3].lower()
        cmd.extend([f'-metadata:s:s:{i}', f'language={lang_code}'])
        cmd.extend([f'-metadata:s:s:{i}', f'title={sub["lang"]}'])
        # Set handler name as well for some players
        cmd.extend([f'-metadata:s:s:{i}', f'handler_name={sub["lang"]}'])

    # Run ffmpeg
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            # Success
            if os.path.exists(video_path):
                os.remove(video_path)
            os.rename(output_path, video_path)
            print("Subtitles embedded successfully.")
        else:
            print(f"FFmpeg failed: {stderr.decode()}")
            if os.path.exists(output_path):
                os.remove(output_path)

    except Exception as e:
        print(f"Embedding failed: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return video_path
