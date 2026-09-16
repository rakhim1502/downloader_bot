# services/downloader.py
import os
import logging
import aiohttp
from dataclasses import dataclass
from enum import Enum

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

class MediaType(Enum):
    VIDEO = "video"
    PHOTO = "photo"

@dataclass
class MediaInfo:
    url: str
    media_type: MediaType
    title: str = ""
    author: str = ""
    file_path: str = ""
    filesize: int = 0
    is_carousel: bool = False
    carousel_items: list = None
    platform: str = ""

class MediaDownloader:
    async def download(self, url: str, platform: str, status_callback=None) -> MediaInfo:
        """
        URL va platformaga qarab meidani yuklab oladi va MediaInfo qaytaradi.
        """
        if status_callback:
            await status_callback("📥 Serverdan media ma'lumotlari olinmoqda...")

        if platform == "instagram":
            return await self._download_instagram(url)
        # Boshqa platformalar uchun (tiktok, youtube va h.k.) logic...
        
        return None

    async def _download_instagram(self, url: str) -> MediaInfo:
        endpoint = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
        }
        params = {"url": url}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        download_url = data.get("download_url") or data.get("url")
                        
                        if download_url:
                            return MediaInfo(
                                url=download_url,
                                media_type=MediaType.VIDEO,
                                title=data.get("title", ""),
                                author=data.get("author", ""),
                                platform="instagram"
                            )
        except Exception as e:
            logging.error(f"Instagram yuklashda xatolik: {e}")
        return None

    async def cleanup(self, media_info: MediaInfo):
        """Vaqtincha saqlangan fayllarni o'chirish."""
        if media_info and media_info.file_path and os.path.exists(media_info.file_path):
            try:
                os.remove(media_info.file_path)
            except Exception as e:
                logging.error(f"Faylni o'chirishda xatolik: {e}")