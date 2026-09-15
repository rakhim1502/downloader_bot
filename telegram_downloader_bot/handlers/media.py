"""
Media handler - Instagram, TikTok va YouTube havolalarini qayta ishlash.
"""
import asyncio
import html
import logging
import os

from aiogram import F, Router
from aiogram.types import FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

from config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from services.downloader import MediaDownloader, MediaInfo, MediaType
from utils.url_parser import PlatformType, URLParser

media_router = Router()
logger = logging.getLogger(__name__)

# Downloader instansiyasini yaratish
downloader = MediaDownloader()


async def send_status_message(message: Message, text: str) -> None:
    """
    Holat xabarini yuboradi yoki yangilaydi.
    """
    try:
        await message.answer(text=text)
    except Exception as e:
        logger.error(f"Holat xabarini yuborishda xatolik: {e}")


@media_router.message(F.text)
async def handle_media_url(message: Message) -> None:
    """
    Foydalanuvchidan kelgan havolani qayta ishlaydi.
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
                f"❌ Qo'llab-quvvatlanmaydigan havola: `{html.escape(url_info['url'])}`\n\n"
                "Faqat Instagram, TikTok va YouTube havolalari ishlaydi.",
                parse_mode="Markdown",
            )
            continue

        platform = url_info["platform"]
        url = url_info["url"]

        # Platforma emojisi
        platform_emoji = {
            "instagram": "📸",
            "tiktok": "🎵",
            "youtube": "📺",
        }.get(platform, "🔗")

        # Status xabari yuborish
        status_msg = await message.answer(
            f"{platform_emoji} **{platform.title()}**\n\n"
            "📥 Havola ishlanmoqda...\n"
            "⏳ Biroz kuting...",
            parse_mode="Markdown",
        )

        try:
            # Holatni yangilash uchun callback
            async def update_status(status_text: str):
                try:
                    await status_msg.edit_text(
                        text=f"{platform_emoji} **{platform.title()}**\n\n{status_text}",
                        parse_mode="Markdown",
                    )
                except Exception:
                    pass

            media_info: MediaInfo = await downloader.download(
                url=url,
                platform=platform,
                status_callback=update_status,
            )

            if not media_info:
                await status_msg.edit_text(
                    "❌ **Xatolik!**\n\n"
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
                total_size = sum(
                    os.path.getsize(f)
                    for f in media_info.carousel_items
                    if os.path.exists(f)
                )
            else:
                total_size = media_info.filesize or (
                    os.path.getsize(media_info.file_path)
                    if media_info.file_path and os.path.exists(media_info.file_path)
                    else 0
                )

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
                await downloader.cleanup(media_info)
                continue

            # Telegramga yuborish haqida xabar
            title_preview = (
                media_info.title[:50] + "..."
                if media_info.title and len(media_info.title) > 50
                else (media_info.title or "Noma'lum")
            )
            await status_msg.edit_text(
                f"✅ **Tayyor!**\n\n"
                f"📝 Nom: {html.escape(title_preview)}\n"
                f"👤 Muallif: {html.escape(media_info.author or 'Noma\'lum')}\n"
                f"📊 Hajm: {total_size / 1024 / 1024:.1f} MB\n\n"
                "📤 Telegramga yuborilmoqda...",
                parse_mode="Markdown",
            )

            # Karusel yoki bittalik media yuborish
            if media_info.is_carousel and media_info.carousel_items:
                await send_carousel(message, media_info)
            else:
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
                f"Xabar: {html.escape(str(e)[:200])}\n\n"
                "Iltimos, keyinroq qayta urinib ko'ring.",
                parse_mode="Markdown",
            )


async def send_video(message: Message, media_info: MediaInfo) -> None:
    try:
        video_file = FSInputFile(media_info.file_path)

        caption = f"🎬 <b>{html.escape(media_info.title or '')}</b>"
        if media_info.author:
            caption += f"\n👤 <b>Muallif:</b> {html.escape(media_info.author)}"

        await message.answer_video(
            video=video_file,
            caption=caption[:1024],  # Telegram caption limiti 1024 belgi
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Video yuborishda xatolik: {e}")
        safe_error_text = html.escape(str(e))
        await message.answer(
            f"❌ Video yuborishda xatolik: {safe_error_text}",
            parse_mode="HTML",
        )


async def send_photo(message: Message, media_info: MediaInfo) -> None:
    try:
        photo_file = FSInputFile(media_info.file_path)
        author_name = media_info.author if media_info.author else "Noma'lum"

        caption = (
            f"📷 <b>{html.escape((media_info.title or '')[:100])}</b>\n\n"
            f"👤 <b>Muallif:</b> {html.escape(author_name)}\n"
            f"🔗 <b>Platforma:</b> {html.escape(str(media_info.platform).title())}"
        )

        await message.answer_photo(
            photo=photo_file,
            caption=caption,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Rasm yuborishda xatolik: {e}")
        await message.answer(
            f"❌ Rasm yuborishda xatolik: {html.escape(str(e))}",
            parse_mode="HTML",
        )


async def send_carousel(message: Message, media_info: MediaInfo) -> None:
    """
    Instagram karusel (ko'p media) ni Telegram Media Group (albom) shaklida yuboradi.
    """
    try:
        if not media_info.carousel_items:
            await message.answer("❌ Karusel elementlari topilmadi.")
            return

        media_group = MediaGroupBuilder()
        author_name = media_info.author if media_info.author else "Noma'lum"
        main_caption = (
            f"📱 <b>{html.escape((media_info.title or '')[:100])}</b>\n"
            f"👤 <b>Muallif:</b> {html.escape(author_name)}"
        )

        # Telegram bitta media guruhda maksimum 10 ta fayl qabul qiladi
        items = media_info.carousel_items[:10]

        for idx, file_path in enumerate(items):
            if not os.path.exists(file_path):
                continue

            file_input = FSInputFile(file_path)
            is_video = file_path.lower().endswith((".mp4", ".webm", ".mov"))

            # Faqat birinchi media-faylga caption beriladi
            caption = main_caption if idx == 0 else None

            if is_video:
                media_group.add_video(media=file_input, caption=caption, parse_mode="HTML")
            else:
                media_group.add_photo(media=file_input, caption=caption, parse_mode="HTML")

        await message.answer_media_group(media=media_group.build())

    except Exception as e:
        logger.error(f"Karusel yuborishda xatolik: {e}")
        await message.answer(
            f"❌ Karusel yuborishda xatolik: {html.escape(str(e))}",
            parse_mode="HTML",
        )