from yt_dlp import YoutubeDL as YoutubeDL

'''
Specifically for Instagram downloads
It just extracts the link, rather than downloading the media
and passes it back to the main bot as telegram support url uploads
'''

def extract_instagram_url(url: str) -> str | None:
    options = {
        'quiet': True,
        'skip_download': True,
        'forceurl': True,
        'noplaylist': True,
        #
        "sleep_requests": 1,
        "sleep_interval": 3,
        "max_sleep_interval": 6,
        'cookiefile': 'cookies/instagram_cookies.txt',  # Path to your Instagram cookies file
    }

    with YoutubeDL(options) as ytdlp:
        try:
            info = ytdlp.extract_info(url, download=False)

            # Logic to find the best progressive (combined audio+video) format
            formats = info.get('formats', [])
            target_url = None

            # 1st pass: look for a format with formatid present, if yes send that, if mutliple send with the lower int value
            for f in formats:
                format_id = f.get('format_id', '')
                if format_id and format_id.isdigit():
                    target_url = f.get('url')
                    break

            # 2nd pass: Look for a format with both video and audio codecs
            for f in formats:
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')
                if vcodec != 'none' and acodec != 'none':
                    target_url = f.get('url')
                    # Prefer higher resolution? Usually the last one is best in yt-dlp formats list
                    # But let's keep iterating to find the best one

            # 3rd pass: If no combined format found, look for non-DASH video
            # (As per user observation, sometimes combined file has missing audio metadata or is just the progressive fallback)
            if not target_url:
                for f in formats:
                    format_id = f.get('format_id', '')
                    format_note = f.get('format_note', '')
                    vcodec = f.get('vcodec', 'none')

                    # Skip DASH formats
                    if 'dash' in format_id.lower() or 'dash' in format_note.lower():
                        continue

                    # Must have video
                    if vcodec == 'none':
                        continue

                    target_url = f.get('url')
                    # Again, keep iterating to find the best one (usually sorted by quality)

            # Fallback: If still nothing, check if 'url' is in top level info (sometimes happens for images or simple videos)
            if not target_url:
                target_url = info.get('url')

            if target_url:
                extracted = {
                    "status": "success",
                    "isUrl": True,
                    "url": target_url, # Use 'url' key as expected by router
                    "filepath": target_url, # For compatibility
                    "filename": info.get('title', 'instagram_media'),
                    "description": info.get('description', ''),
                    "title": info.get('fulltitle', ''),
                    "thumbnail": info.get('thumbnail', ''),
                    "resolution": info.get('resolution', 'NonexNone'),
                    "duration": info.get('duration'),
                    "original_url": info.get('webpage_url', url),
                    "type": "video" if info.get('ext') in ['mp4', 'mov'] else "image",
                    # "info": info
                 }
                return extracted
            else:
                return None
        except Exception as e:
            print(f"Error extracting Instagram URL: {e}")
            return None
