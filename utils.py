import os
import re
import shutil
import instaloader
from typing import Tuple, List, Optional

def extract_post_id(url: str) -> Optional[str]:
    """
    Extract shortcode (post_id) from Instagram URL
    Example: https://www.instagram.com/reel/ABC123/ → ABC123
    """
    match = re.search(r'instagram\.com/(?:p|reel)/([A-Za-z0-9-_]+)', url)
    return match.group(1) if match else None


async def download_post(post_id: str, username: str = None, password: str = None) -> Tuple[List[str], List[str], str]:
    """
    Download photos/videos from an Instagram post using Instaloader
    """
    loader = instaloader.Instaloader(
        quiet=True,
        download_pictures=True,
        download_videos=True,
        save_metadata=False,
        post_metadata_txt_pattern=""  # avoid extra .txt metadata
    )

    # Login if credentials provided
    if username and password:
        try:
            loader.login(username, password)
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")

    try:
        # Fix: use Post.from_shortcode instead of wrong download_post
        post = instaloader.Post.from_shortcode(loader.context, post_id)
        loader.download_post(post, target=f"-{post_id}")
    except instaloader.exceptions.LoginRequiredException:
        raise Exception("Private post - requires Instagram login")
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

    photos = []
    videos = []
    caption = post.caption if post.caption else ""

    # Collect media files
    for file in os.listdir(f"-{post_id}"):
        file_path = os.path.join(f"-{post_id}", file)
        if file.endswith(".jpg"):
            photos.append(file_path)
        elif file.endswith(".mp4"):
            videos.append(file_path)

    return photos, videos, caption


async def cleanup(path: str):
    """Remove temporary download folder"""
    if os.path.exists(path):
        shutil.rmtree(path)
