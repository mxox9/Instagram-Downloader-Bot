import requests
import re

def get_instagram_media(url: str):
    """
    Try to extract media (video/image) from Instagram public URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            raise Exception("Failed to fetch page")

        html = r.text

        # Try to find video
        video_match = re.search(r'"video_url":"([^"]+)"', html)
        if video_match:
            video_url = video_match.group(1).replace("\\u0026", "&").replace("\\/", "/")
            return {"type": "video", "url": video_url}

        # Try to find image
        image_match = re.search(r'"display_url":"([^"]+)"', html)
        if image_match:
            img_url = image_match.group(1).replace("\\u0026", "&").replace("\\/", "/")
            return {"type": "photo", "url": img_url}

        return None
    except Exception as e:
        print("Error:", e)
        return None
