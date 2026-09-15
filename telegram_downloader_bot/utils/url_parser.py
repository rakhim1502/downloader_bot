"""
URL Parser - Instagram, TikTok va YouTube havolalarini ajratib olish va tekshirish.
"""
import re
from typing import Optional, Dict, List
from enum import Enum


class PlatformType(Enum):
    """Qo'llab-quvvatlanadigan platformalar."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    UNKNOWN = "unknown"


class URLParser:
    """URL havolalarni tahlil qilish va platformani aniqlash."""

    # Regex patternlar
    PATTERNS = {
        PlatformType.INSTAGRAM: re.compile(
            r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/'
            r'(reel|reels|p|tv)/([a-zA-Z0-9_\-]+)',
            re.IGNORECASE
        ),
        PlatformType.TIKTOK: re.compile(
            r'(https?://)?(www\.)?(tiktok\.com)/(@[\w\.]+)/video/(\d+)',
            re.IGNORECASE
        ),
        PlatformType.YOUTUBE: re.compile(
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
            r'(watch\?v=|shorts/|embed/)?([a-zA-Z0-9_\-]+)',
            re.IGNORECASE
        ),
    }

    @classmethod
    def extract_urls(cls, text: str) -> List[str]:
        """
        Matndan barcha URL havolalarni ajratib oladi.
        
        Args:
            text: Matn qatori
            
        Returns:
            URL havolalar ro'yxati
        """
        url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE
        )
        return url_pattern.findall(text)

    @classmethod
    def detect_platform(cls, url: str) -> PlatformType:
        """
        URL orqali platformani aniqlaydi.
        
        Args:
            url: Havola
            
        Returns:
            PlatformType enum qiymati
        """
        for platform, pattern in cls.PATTERNS.items():
            if pattern.search(url):
                return platform
        return PlatformType.UNKNOWN

    @classmethod
    def is_supported(cls, url: str) -> bool:
        """
        URL qo'llab-quvvatlanadigan platformaga tegishli ekanligini tekshiradi.
        
        Args:
            url: Havola
            
        Returns:
            True agar qo'llab-quvvatlansa, False aks holda
        """
        return cls.detect_platform(url) != PlatformType.UNKNOWN

    @classmethod
    def validate_url(cls, url: str) -> Dict:
        """
        URL havolasini to'liq tekshiradi va ma'lumotlarni qaytaradi.
        
        Args:
            url: Havola
            
        Returns:
            Dict with keys: valid, platform, url
        """
        platform = cls.detect_platform(url)
        is_valid = platform != PlatformType.UNKNOWN
        
        return {
            "valid": is_valid,
            "platform": platform.value if is_valid else None,
            "url": url,
            "error": None if is_valid else "Noto'g'ri yoki qo'llab-quvvatlanmaydigan havola"
        }

    @classmethod
    def parse_message(cls, message_text: str) -> List[Dict]:
        """
        Xabar matnidan barcha URL'larni ajratib, ularni tahlil qiladi.
        
        Args:
            message_text: Foydalanuvchi xabari matni
            
        Returns:
            Tahlil qilingan URL'larning ro'yxati
        """
        urls = cls.extract_urls(message_text)
        results = []
        
        for url in urls:
            result = cls.validate_url(url)
            results.append(result)
        
        return results
