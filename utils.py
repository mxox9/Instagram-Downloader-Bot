import os
import re
import shutil
import instaloader
from typing import Tuple, List, Optional

def extract_post_id(url: str) -> Optional[str]:
    match = re.search(r'instagram\.com/(?:p|reel)/([A-Za-z0-9-_]+)', url)
    return match.group(1) if match else None

async def download_post(post_id: str, username: str = None, password: str = None) -> Tuple[List[str], List[str], str]:
    loader = instaloader.Instaloader(
        quiet=True,
        download_pictures=True,
        download_videos=True,
        save_metadata=False
    )
    
    if username and password:
        try:
            loader.login(username, password)
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    try:
        loader.download_post(post_id, target=f"-{post_id}")
    except instaloader.exceptions.LoginRequiredException:
        raise Exception("Private post - requires Instagram login")
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")
    
    photos = []
    videos = []
    caption = ""
    
    for file in os.listdir(f"-{post_id}"):
        file_path = os.path.join(f"-{post_id}", file)
        if file.endswith(".jpg"):
            photos.append(file_path)
        elif file.endswith(".mp4"):
            videos.append(file_path)
        elif file.endswith(".txt"):
            with open(file_path, "r") as f:
                caption = f.read()
    
    return photos, videos, caption

async def cleanup(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
