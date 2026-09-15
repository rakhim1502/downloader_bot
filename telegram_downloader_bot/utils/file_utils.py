"""
Fayl bilan ishlash yordamchi funksiyalari.
"""
import os
import asyncio
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FileUtils:
    """Fayl operatsiyalari uchun yordamchi klass."""

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Fayl hajmini baytlarda qaytaradi.
        
        Args:
            file_path: Fayl yo'li
            
        Returns:
            Fayl hajmi (bytes)
        """
        return os.path.getsize(file_path)

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        Fayl hajmini MB da qaytaradi.
        
        Args:
            file_path: Fayl yo'li
            
        Returns:
            Fayl hajmi (MB)
        """
        return os.path.getsize(file_path) / (1024 * 1024)

    @staticmethod
    def check_file_size(file_path: str, max_size_mb: int = 50) -> bool:
        """
        Fayl hajmini tekshiradi.
        
        Args:
            file_path: Fayl yo'li
            max_size_mb: Maksimal hajm (MB)
            
        Returns:
            True agar hajm me'yorida bo'lsa, False aks holda
        """
        size_mb = FileUtils.get_file_size_mb(file_path)
        return size_mb <= max_size_mb

    @staticmethod
    async def ensure_dir(directory: str) -> None:
        """
        Papka mavjudligini tekshiradi va agar yo'q bo'lsa yaratadi.
        
        Args:
            directory: Papka yo'li
        """
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Papka yaratildi: {directory}")

    @staticmethod
    async def safe_remove(file_path: str) -> bool:
        """
        Faylni xavfsiz o'chiradi.
        
        Args:
            file_path: Fayl yo'li
            
        Returns:
            True agar o'chirish muvaffaqiyatli bo'lsa
        """
        try:
            if os.path.exists(file_path):
                await asyncio.to_thread(os.remove, file_path)
                logger.debug(f"Fayl o'chirildi: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Faylni o'chirishda xatolik: {file_path} - {e}")
            return False

    @staticmethod
    async def cleanup_files(file_paths: list) -> None:
        """
        Bir nechta fayllarni tozalaydi.
        
        Args:
            file_paths: Fayl yo'llari ro'yxati
        """
        for file_path in file_paths:
            await FileUtils.safe_remove(file_path)

    @staticmethod
    def generate_filename(platform: str, media_type: str = "video") -> str:
        """
        Unikal fayl nomi generatsiya qiladi.
        
        Args:
            platform: Platforma nomi (instagram, tiktok, youtube)
            media_type: Media turi (video, image)
            
        Returns:
            Fayl nomi
        """
        import time
        timestamp = int(time.time())
        extension = "mp4" if media_type == "video" else "jpg"
        return f"{platform}_{media_type}_{timestamp}.{extension}"
