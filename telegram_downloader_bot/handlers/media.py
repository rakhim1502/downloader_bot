"""
Media handler - Instagram, TikTok va YouTube havolalarini qayta ishlash.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message

from config import MAX_FILE_SIZE_MB, MAX_FILE_SIZE_BYTES
from utils.url_parser import URLParser, PlatformType
from services.downloader import MediaDownloader, MediaType

media_router = Router()
logger = logging.getLogger(__name__)

# Downloader instansini yaratish
downloader = MediaDownloader()


async def send_status_message(message: Message, text: str) -> None:
    """
    Holat xabarini yuboradi yoki yangilaydi.
    
    Args:
        message: Asl xabar
        text: Yangi holat matni
    """
    try:
        await message.answer(text=text)
    except Exception as e:
        logger.error(f"Holat xabarini yuborishda xatolik: {e}")


@media_router.message(F.text)
async def handle_media_url(message: Message) -> None:
    """
    Foydalanuvchidan kelgan havolani qayta ishlaydi.
    
    Args:
        message: Xabar obyekti
    """
    text = message.text.strip()
    
    if not text:
        return
    
    # URL'larni ajratib olish
    parsed_urls = URLParser.parse_message(text)
    
    if not parsed_urls:
        await message.answer(
            "❌ Noto'g'ri havola. Iltimos, Instagram, TikTok yoki YouTube havolasini yuboring.\n\n"
            "Misol:\n"
            "• https://instagram.com/reel/ABC123\n"
            "• https://tiktok.com/@user/video/123456\n"
            "• https://youtube.com/shorts/ABC123"
        )
        return
    
    # Har bir URL uchun alohida ishlov berish
    for url_info in parsed_urls:
        if not url_info["valid"]:
            await message.answer(
                f"❌ Qo'llab-quvvatlanmaydigan havola: `{url_info['url']}`\n\n"
                "Faqat Instagram, TikTok va YouTube havolalari ishlaydi.",
                parse_mode="Markdown",
            )
            continue
        
        platform = url_info["platform"]
        url = url_info["url"]
        
        # Platforma nomi chiroyli ko'rinishi
        platform_emoji = {
            "instagram": "📸",
            "tiktok": "🎵",
            "youtube": "📺",
        }.get(platform, "🔗")
        
        # Status xabari yuborish
        status_msg = await message.answer(
            f"{platform_emoji} **{platform.title()}**\n\n"
            "📥 Havola ishlanmoqda...\n"
            "⏳ Biroz kuting..."
        )
        
        try:
            # Media yuklash
            async def update_status(status_text: str):
                """Holatni yangilash uchun callback."""
                try:
                    await status_msg.edit_text(
                        text=f"{platform_emoji} **{platform.title()}**\n\n{status_text}",
                        parse_mode="Markdown",
                    )
                except Exception:
                    # Agar edit qilib bo'lmasa, yangi xabar yuborish
                    pass
            
            media_info = await downloader.download(
                url=url,
                platform=platform,
                status_callback=update_status,
            )
            
            if not media_info:
                await status_msg.edit_text(
                    f"❌ **Xatolik!**\n\n"
                    "Video yuklanmadi. Sabablari:\n"
                    "• Havola noto'g'ri yoki eskirgan\n"
                    "• Profil yopiq (private)\n"
                    "• Video o'chirilgan\n\n"
                    "Boshqa havolani urinib ko'ring.",
                    parse_mode="Markdown",
                )
                continue
            
            # Fayl hajmini tekshirish
            if media_info.is_carousel and media_info.carousel_items:
                # Karusel uchun har bir faylni tekshirish
                total_size = sum(
                    os.path.getsize(f) for f in media_info.carousel_items 
                    if os.path.exists(f)
                )
            else:
                total_size = media_info.filesize or 0
            
            if total_size > MAX_FILE_SIZE_BYTES:
                size_mb = total_size / (1024 * 1024)
                await status_msg.edit_text(
                    f"⚠️ **Fayl hajmi juda katta!**\n\n"
                    f"Hajm: {size_mb:.1f} MB\n"
                    f"Maksimal ruxsat: {MAX_FILE_SIZE_MB} MB\n\n"
                    "Telegram Bot API cheklovi tufayli bu faylni yubora olmayman.\n"
                    "Iltimos, boshqa videoni tanlang.",
                    parse_mode="Markdown",
                )
                # Faylni tozalash
                await downloader.cleanup(media_info)
                continue
            
            # Telegramga yuborish
            await status_msg.edit_text(
                f"✅ **Tayyor!**\n\n"
                f"📝 Nom: {media_info.title[:50]}{'...' if len(media_info.title) > 50 else ''}\n"
                "👤 Muallif: " + (media_info.author or "Noma'lum") + "\n"
                f"📊 Hajm: {total_size / 1024 / 1024:.1f} MB\n\n"
                "📤 Telegramga yuborilmoqda...",
                parse_mode="Markdown",
            )
            
            # Karusel yoki oddiy video/rasm
            if media_info.is_carousel and media_info.carousel_items:
                # Ko'p mediali post (Instagram carousel)
                await send_carousel(message, media_info)
            else:
                # Bitta video yoki rasm
                if media_info.media_type == MediaType.VIDEO:
                    await send_video(message, media_info)
                else:
                    await send_photo(message, media_info)
            
            # Yakuniy xabar
            await message.answer(
                "✅ Yuklash muvaffaqiyatli amalga oshirildi!\n\n"
                "Yana havola yuboring 👇"
            )
            
            # Fayllarni tozalash
            await downloader.cleanup(media_info)
            
        except Exception as e:
            logger.error(f"Media qayta ishlashda xatolik: {e}", exc_info=True)
            await status_msg.edit_text(
                f"❌ **Kutilmagan xatolik!**\n\n"
                f"Xabar: {str(e)[:200]}\n\n"
                "Iltimos, keyinroq qayta urinib ko'ring.",
                parse_mode="Markdown",
            )


async def send_video(message: Message, media_info) -> None:
    """
    Videoni Telegramga yuboradi.
    
    Args:
        message: Xabar obyekti
        media_info: Media ma'lumotlari
    """
    try:
        author_name = media_info.author if media_info.author else "Noma'lum"
        caption = (
            f"📹 **{media_info.title[:100]}**\n\n"
            f"👤 {author_name}\n"
            f"🔗 Platforma: {media_info.platform.title()}"
        )
        
        with open(media_info.file_path, 'rb') as video_file:
            await message.answer_video(
                video=video_file,
                caption=caption,
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Video yuborishda xatolik: {e}")
        await message.answer(f"❌ Video yuborishda xatolik: {str(e)}")


async def send_photo(message: Message, media_info) -> None:
    """
    Rasmni Telegramga yuboradi.
    
    Args:
        message: Xabar obyekti
        media_info: Media ma'lumotlari
    """
    try:
        author_name = media_info.author if media_info.author else "Noma'lum"
        caption = (
            f"📷 **{media_info.title[:100]}**\n\n"
            f"👤 {author_name}\n"
            f"🔗 Platforma: {media_info.platform.title()}"
        )
        
        with open(media_info.file_path, 'rb') as photo_file:
            await message.answer_photo(
                photo=photo_file,
                caption=caption,
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Rasm yuborishda xatolik: {e}")
        await message.answer(f"❌ Rasm yuborishda xatolik: {str(e)}")


async def send_carousel(message: Message, media_info) -> None:
    """
    Instagram karusel (ko'p media) ni yuboradi.
    
    Args:
        message: Xabar obyekti
        media_info: Media ma'lumotlari (carousel_items bilan)
    """
    try:
        if not media_info.carousel_items:
            await message.answer("❌ Karusel elementlari topilmadi.")
            return
        
        # Har bir elementni alohida yuborish
        for idx, file_path in enumerate(media_info.carousel_items, 1):
            if not os.path.exists(file_path):
                continue
            
            # Fayl turi aniqlash
            is_video = file_path.endswith(('.mp4', '.webm', '.mov'))
            
            author_name = media_info.author if media_info.author else "Noma'lum"
            caption = (
                f"📱 **Karusel {idx}/{len(media_info.carousel_items)}**\n\n"
                f"📷 {media_info.title[:100]}\n"
                f"👤 {author_name}"
            )
            
            if is_video:
                with open(file_path, 'rb') as video_file:
                    await message.answer_video(
                        video=video_file,
                        caption=caption,
                        parse_mode="Markdown",
                    )
            else:
                with open(file_path, 'rb') as photo_file:
                    await message.answer_photo(
                        photo=photo_file,
                        caption=caption,
                        parse_mode="Markdown",
                    )
            
            # Kichik kechikish (rate limit)
            import asyncio
            await asyncio.sleep(0.5)
            
    except Exception as e:
        logger.error(f"Karusel yuborishda xatolik: {e}")
        await message.answer(f"❌ Karusel yuborishda xatolik: {str(e)}")


# Import os module for file operations
import os
