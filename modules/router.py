import os
import sys
import json
import urllib.parse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utils.validator import UrlValidator
from modules.providers.spotify import spotify_provider
from modules.providers.instagram import instagram_provider
from modules.providers.general import general_provider

async def route(url: str, client, message, progress_callback, user_manager, video_id, audio=False, format_id="bestvideo+bestaudio/best", custom_title=None):
    validator = UrlValidator(url)
    result = None

    if validator.isSpotify():
        print("Routing to Spotify provider...")
        # Spotify provider needs to be updated to accept these args or we adapt here
        # Assuming spotify_provider.download is synchronous or async?
        # The previous implementation was synchronous. Let's check if we need to wrap it.
        # But for now, let's assume we might need to update spotify provider too.
        # For now, passing minimal args as it was before, but we should probably update it.
        if not spotify_provider.check_spotdl_installed():
            return {
                "status": "error",
                "message": "SpotDL is not installed or not found in PATH. Please install SpotDL to use the Spotify provider."
            }
        result = spotify_provider.download(url)
    elif validator.isInstagram():
        print("Routing to Instagram provider...")
        result = instagram_provider.extract_instagram_url(url)

    elif validator.isUrl():
        print("Routing to General provider...")
        result = await general_provider.download(url, client, message, progress_callback, user_manager, video_id, audio, format_id, custom_title)
    else:
        return {"status": "error", "message": "Invalid URL"}

    return result
