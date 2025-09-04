import requests
import re

def get_instagram_media(url: str):
    """
    Download public Instagram reels/videos/images without login.
    Works only for PUBLIC posts/reels.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None, "Failed to fetch page"

        # video_url निकालो
        match = re.search(r'"video_url":"([^"]+)"', r.text)
        if match:
            video_url = match.group(1).replace("\\u0026", "&")
            return video_url, None

        # अगर image है
        match_img = re.search(r'"display_url":"([^"]+)"', r.text)
        if match_img:
            image_url = match_img.group(1).replace("\\u0026", "&")
            return image_url, None

        return None, "❌ Media not found (maybe private account?)"

    except Exception as e:
        return None, str(e)
