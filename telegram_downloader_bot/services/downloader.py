"""
Media Downloader Service - YouTube, TikTok va Instagram'dan media yuklash.
yt-dlp kutubxonasidan foydalanadi.
"""
import os
import asyncio
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import yt_dlp

from config import DOWNLOAD_DIR, TEMP_DIR, REQUEST_TIMEOUT
from utils.file_utils import FileUtils

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """Media turlari."""
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"  # Ko'p mediali post


@dataclass
class MediaInfo:
    """Media ma'lumotlari."""
    url: str
    platform: str
    title: str
    media_type: MediaType
    file_path: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None  # soniya
    filesize: Optional[int] = None  # bytes
    author: Optional[str] = None
    description: Optional[str] = None
    is_carousel: bool = False
    carousel_items: Optional[List[str]] = None  # Carousel uchun fayl yo'llari


class MediaDownloader:
    """Media yuklash servisi."""

    def __init__(self):
        self.download_dir = DOWNLOAD_DIR
        self.temp_dir = TEMP_DIR
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Yuklash papkalarini yaratadi."""
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Papkalar tayyorlandi: {self.download_dir}, {self.temp_dir}")

    def _get_ydl_options(self, platform: str, output_template: str) -> Dict:
        """
        Platformaga mos yt-dlp sozlamalarini qaytaradi.
        
        Args:
            platform: Platforma nomi (instagram, tiktok, youtube)
            output_template: Fayl nomi shabloni
            
        Returns:
            yt-dlp options dict
        """
        base_options = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': REQUEST_TIMEOUT,
            'retries': 3,
        }

        # TikTok: suv belgisiz (no watermark) video
        if platform == "tiktok":
            base_options.update({
                'format': 'best',
                'prefer_free_formats': False,
                # TikTok maxsus sozlamalari
                'extractor_args': {
                    'tiktok': {
                        'api_hostname': ['api16-normal-c-useast1a.tiktokv.com'],
                    }
                },
            })
        # Instagram: reels, posts, carousel
        elif platform == "instagram":
            base_options.update({
                'format': 'best',
                # Instagram carousel uchun
                'extract_flat': False,
            })
        # YouTube: Shorts va oddiy videolar
        elif platform == "youtube":
            base_options.update({
                'format': 'best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })

        return base_options

    async def download_video(
        self,
        url: str,
        platform: str,
        status_callback=None
    ) -> Optional[MediaInfo]:
        """
        Videoni yuklab oladi.
        
        Args:
            url: Video havolasi
            platform: Platforma nomi
            status_callback: Holat xabarlari uchun callback funksiyasi
            
        Returns:
            MediaInfo obyekti yoki None (xatolik bo'lsa)
        """
        if status_callback:
            await status_callback("📥 Havola ishlanmoqda...")

        try:
            # Fayl nomini generatsiya qilish
            filename = FileUtils.generate_filename(platform, "video")
            output_template = os.path.join(self.download_dir, filename)

            if status_callback:
                await status_callback("⬇️ Video yuklanmoqda...")

            # yt-dlp sozlamalari
            ydl_opts = self._get_ydl_options(platform, output_template)

            # Asinxron ravishda yuklash
            loop = asyncio.get_event_loop()
            
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return info

            info = await loop.run_in_executor(None, _download)

            if not info:
                logger.error("Video ma'lumotlari olinmadi")
                return None

            # Fayl yo'lini aniqlash
            file_path = info.get('filepath', '')
            
            # Agar fayl mavjud bo'lmasa, boshqa variantlarni tekshirish
            if not file_path or not os.path.exists(file_path):
                # Fallback: eng yaqin faylni topish
                base_name = os.path.splitext(output_template)[0]
                for ext in ['.mp4', '.webm', '.mkv', '.mov']:
                    test_path = f"{base_name}{ext}"
                    if os.path.exists(test_path):
                        file_path = test_path
                        break

            if not file_path or not os.path.exists(file_path):
                logger.error(f"Yuklangan fayl topilmadi: {output_template}")
                return None

            if status_callback:
                await status_callback("✅ Video tayyor!")

            # Media ma'lumotlarini to'plash
            media_info = MediaInfo(
                url=url,
                platform=platform,
                title=info.get('title', 'Noma\'lum'),
                media_type=MediaType.VIDEO,
                file_path=file_path,
                thumbnail=info.get('thumbnail'),
                duration=info.get('duration'),
                filesize=os.path.getsize(file_path),
                author=info.get('uploader', info.get('channel')),
                description=info.get('description', ''),
            )

            logger.info(f"Video yuklandi: {file_path} ({media_info.filesize} bytes)")
            return media_info

        except Exception as e:
            logger.error(f"Video yuklashda xatolik: {e}", exc_info=True)
            if status_callback:
                await status_callback(f"❌ Xatolik: {str(e)[:100]}")
            return None

    async def download_instagram_carousel(
        self,
        url: str,
        status_callback=None
    ) -> Optional[MediaInfo]:
        """
        Instagram karusel (ko'p mediali post) ni yuklaydi.
        
        Args:
            url: Instagram post havolasi
            status_callback: Holat xabarlari uchun callback
            
        Returns:
            MediaInfo obyekti (carousel_items bilan) yoki None
        """
        if status_callback:
            await status_callback("📥 Karusel ishlanmoqda...")

        try:
            output_template = os.path.join(
                self.download_dir,
                f"instagram_carousel_{int(asyncio.get_event_loop().time())}_%(entry_number)d.%(ext)s"
            )

            if status_callback:
                await status_callback("⬇️ Karusel elementlari yuklanmoqda...")

            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': REQUEST_TIMEOUT,
                'retries': 3,
                # Playlist/Carousel uchun
                'playlistend': 20,  # Maksimum 20 ta element
            }

            loop = asyncio.get_event_loop()
            
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return info

            info = await loop.run_in_executor(None, _download)

            if not info:
                return None

            # Carousel elementlarini yig'ish
            carousel_items = []
            entries = info.get('entries', [info])  # Agar bitta entry bo'lsa ham

            for entry in entries:
                if entry:
                    filepath = entry.get('filepath', '')
                    if filepath and os.path.exists(filepath):
                        carousel_items.append(filepath)

            if not carousel_items:
                logger.error("Karusel elementlari topilmadi")
                return None

            if status_callback:
                await status_callback(f"✅ {len(carousel_items)} ta media yuklandi!")

            media_info = MediaInfo(
                url=url,
                platform="instagram",
                title=info.get('title', 'Instagram Karusel'),
                media_type=MediaType.CAROUSEL,
                file_path=carousel_items[0] if carousel_items else '',
                thumbnail=info.get('thumbnail'),
                author=info.get('uploader'),
                is_carousel=True,
                carousel_items=carousel_items,
            )

            logger.info(f"Karusel yuklandi: {len(carousel_items)} element")
            return media_info

        except Exception as e:
            logger.error(f"Karusel yuklashda xatolik: {e}", exc_info=True)
            if status_callback:
                await status_callback(f"❌ Xatolik: {str(e)[:100]}")
            return None

    async def download(
        self,
        url: str,
        platform: str,
        status_callback=None
    ) -> Optional[MediaInfo]:
        """
        Universal yuklash funksiyasi.
        Platformaga qarab tegishli metodni chaqiradi.
        
        Args:
            url: Media havolasi
            platform: Platforma nomi
            status_callback: Holat xabarlari uchun callback
            
        Returns:
            MediaInfo obyekti yoki None
        """
        try:
            # Instagram karusel ekanligini tekshirish
            if platform == "instagram":
                # Avval ma'lumotlarni olish
                loop = asyncio.get_event_loop()
                
                def _extract_info():
                    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': False}) as ydl:
                        return ydl.extract_info(url, download=False)
                
                try:
                    info = await loop.run_in_executor(None, _extract_info)
                    is_carousel = info.get('entry_count', 0) > 1 or 'entries' in info
                    
                    if is_carousel:
                        return await self.download_instagram_carousel(url, status_callback)
                except Exception:
                    pass  # Oddiy video sifatida davom etish

            # Oddiy video yuklash
            return await self.download_video(url, platform, status_callback)

        except Exception as e:
            logger.error(f"Yuklashda umumiy xatolik: {e}", exc_info=True)
            if status_callback:
                await status_callback(f"❌ Xatolik: {str(e)[:100]}")
            return None

    async def cleanup(self, media_info: MediaInfo) -> None:
        """
        Yuklangan fayllarni tozalaydi.
        
        Args:
            media_info: Media ma'lumotlari
        """
        files_to_clean = []
        
        if media_info.is_carousel and media_info.carousel_items:
            files_to_clean.extend(media_info.carousel_items)
        elif media_info.file_path:
            files_to_clean.append(media_info.file_path)
        
        if media_info.thumbnail:
            files_to_clean.append(media_info.thumbnail)
        
        await FileUtils.cleanup_files(files_to_clean)
        logger.debug(f"Fayllar tozalandi: {files_to_clean}")
