"""
/start va /help buyruqlari handlerlari.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    /start buyrug'i uchun handler.
    Bot haqida ma'lumot beradi.
    """
    welcome_text = (
        "👋 **Assalomu alaykum!**\n\n"
        "Men Instagram, TikTok va YouTube'dan video va rasmlarni yuklab beruvchi botman.\n\n"
        "📱 **Qo'llab-quvvatlanadigan platformalar:**\n"
        "• Instagram (Reels, Post, Karusel)\n"
        "• TikTok (suv belgisiz / no watermark)\n"
        "• YouTube (Shorts, Video)\n\n"
        "🚀 **Foydalanish:**\n"
        "Shunchaki havolani menga yuboring, men uni yuklab olaman!\n\n"
        "⚠️ **Eslatma:**\n"
        "• Maksimal fayl hajmi: 50MB\n"
        "• Katta hajmli videolar uchun ogohlantirish beriladi\n\n"
        "🆘 Yordam uchun /help buyrug'ini yuboring."
    )
    
    await message.answer(
        text=welcome_text,
        parse_mode="Markdown",
    )


@start_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    /help buyrug'i uchun handler.
    Foydalanish bo'yicha qo'llanma.
    """
    help_text = (
        "📚 **Yordam**\n\n"
        "**Qanday ishlatish kerak?**\n"
        "1. Instagram, TikTok yoki YouTube havolasini nusxalang\n"
        "2. Menga yuboring\n"
        "3. Men media yuklab olaman va sizga yuboraman\n\n"
        "**Misol havolalar:**\n"
        "• Instagram: `https://instagram.com/reel/ABC123`\n"
        "• TikTok: `https://tiktok.com/@user/video/123456`\n"
        "• YouTube: `https://youtube.com/shorts/ABC123`\n\n"
        "**Buyruqlar:**\n"
        "/start - Botni ishga tushirish\n"
        "/help - Ushbu yordam xabari\n"
        "/stats - Statistika (tez orada)\n\n"
        "❓ Savollaringiz bormi? @admin ga murojaat qiling."
    )
    
    await message.answer(
        text=help_text,
        parse_mode="Markdown",
    )


@start_router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """
    /stats buyrug'i uchun handler.
    Bot statistikasi (hozircha oddiy).
    """
    stats_text = (
        "📊 **Bot Statistikasi**\n\n"
        "Hozircha faqat asosiy funksiyalar ishlaydi.\n"
        "Tez orada batafsil statistika qo'shiladi.\n\n"
        "✅ Bot ish holatida!"
    )
    
    await message.answer(
        text=stats_text,
        parse_mode="Markdown",
    )
