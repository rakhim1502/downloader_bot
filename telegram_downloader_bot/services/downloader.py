"""
Media Downloader Service - YouTube, TikTok va Instagram'dan media yuklash.
yt-dlp kutubxonasidan foydalanadi.
"""
import os
import asyncio
import logging
import uuid
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

    def _get_ydl_options(self, platform: str, output_template: str) -> Dict[str, Any]:
        """Platformaga mos yt-dlp sozlamalarini qaytaradi."""
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
                'extract_flat': False,
            })
        # YouTube: Shorts va oddiy videolar
        elif platform == "youtube":
            base_options.update({
                'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                'merge_output_format': 'mp4',
            })

        return base_options

    async def download_video(
        self,
        url: str,
        platform: str,
        status_callback=None
    ) -> Optional[MediaInfo]:
        """Videoni yuklab oladi."""
        if status_callback:
            await status_callback("📥 Havola ishlanmoqda...")

        try:
            filename = FileUtils.generate_filename(platform, "video")
            output_template = os.path.join(self.download_dir, filename)

            if status_callback:
                await status_callback("⬇️ Video yuklanmoqda...")

            ydl_opts = self._get_ydl_options(platform, output_template)
            loop = asyncio.get_running_loop()

            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    # Real fayl yo'lini aniqlash
                    file_path = ydl.prepare_filename(info)
                    return info, file_path

            info, file_path = await loop.run_in_executor(None, _download)

            if not info:
                logger.error("Video ma'lumotlari olinmadi")
                return None

            # Agar ko'rsatilgan kengaytma mos kelmasa fallback
            if not os.path.exists(file_path):
                base_name = os.path.splitext(file_path)[0]
                for ext in ['.mp4', '.mkv', '.webm', '.mov']:
                    if os.path.exists(base_name + ext):
                        file_path = base_name + ext
                        break

            if not os.path.exists(file_path):
                logger.error(f"Yuklangan fayl topilmadi: {output_template}")
                return None

            if status_callback:
                await status_callback("✅ Video tayyor!")

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
        """Instagram karusel (ko'p mediali post) ni yuklaydi."""
        if status_callback:
            await status_callback("📥 Karusel ishlanmoqda...")

        try:
            unique_id = uuid.uuid4().hex[:8]
            output_template = os.path.join(
                self.download_dir,
                f"instagram_carousel_{unique_id}_%(playlist_index)s.%(ext)s"
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
                'playlistend': 20,
            }

            loop = asyncio.get_running_loop()

            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    carousel_files = []
                    entries = info.get('entries', [info]) if info else []
                    
                    for entry in entries:
                        if entry:
                            # yt-dlp tomonidan tayyorlangan fayl yo'li
                            fp = ydl.prepare_filename(entry)
                            if os.path.exists(fp):
                                carousel_files.append(fp)
                            else:
                                # Fallback kengaytma izlash
                                base = os.path.splitext(fp)[0]
                                for ext in ['.jpg', '.png', '.mp4', '.webp']:
                                    if os.path.exists(base + ext):
                                        carousel_files.append(base + ext)
                                        break

                    return info, carousel_files

            info, carousel_items = await loop.run_in_executor(None, _download)

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
                file_path=carousel_items[0],
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
        """Universal yuklash funksiyasi."""
        # Instagram uchun to'g'ridan-to'g me'yoriy tekshiruv o'rniga yagona kirish nuqtasi
        if platform == "instagram":
            # Avval Karusel sifatida yuklab ko'rish yaxshiroq natija beradi
            # Chunki karusel bo'lmasa yt-dlp baribir 1 ta fayl yuklaydi
            res = await self.download_instagram_carousel(url, status_callback)
            if res and res.carousel_items and len(res.carousel_items) == 1:
                res.is_carousel = False
                res.media_type = MediaType.VIDEO
            return res if res else await self.download_video(url, platform, status_callback)

        return await self.download_video(url, platform, status_callback)

    async def cleanup(self, media_info: MediaInfo) -> None:
        """Yuklangan fayllarni tozalaydi."""
        if not media_info:
            return

        files_to_clean = []

        if media_info.is_carousel and media_info.carousel_items:
            files_to_clean.extend(media_info.carousel_items)
        elif media_info.file_path:
            files_to_clean.append(media_info.file_path)

        if media_info.thumbnail and os.path.exists(media_info.thumbnail):
            files_to_clean.append(media_info.thumbnail)

        await FileUtils.cleanup_files(files_to_clean)
        logger.debug(f"Fayllar tozalandi: {files_to_clean}")