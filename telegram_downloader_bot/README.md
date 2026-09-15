# Instagram, TikTok va YouTube Video Downloader Telegram Bot

Production-ready Telegram bot - Instagram (Reels, Post, Karusel), TikTok (suv belgisiz) va YouTube (Shorts, Video) dan media yuklab olish uchun.

## 📱 Qo'llab-quvvatlanadigan Platformalar

- **Instagram**: Reels, Posts, Carousel (ko'p mediali postlar)
- **TikTok**: Videolar suv belgisiz (no watermark)
- **YouTube**: Shorts va oddiy videolar

## 🚀 Xususiyatlar

- ✅ Asinxron (async/await) ishlash
- ✅ URL avtomatik aniqlash (Regex parser)
- ✅ TikTok no-watermark yuklash
- ✅ Instagram karusel qo'llab-quvvatlanadi
- ✅ Fayl hajmini tekshirish (50MB limit)
- ✅ Dinamik holat xabarlari
- ✅ To'liq error handling
- ✅ Modulli arxitektura

## 📁 Loyiha Strukturasi

```
telegram_downloader_bot/
├── main.py                 # Bot asosiy fayli
├── config.py               # Konfiguratsiya sozlamalari
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables namunasi
├── handlers/
│   ├── __init__.py
│   ├── start.py           # /start, /help handlerlari
│   └── media.py           # Media URL handlerlari
├── services/
│   ├── __init__.py
│   └── downloader.py      # yt-dlp media downloader
├── utils/
│   ├── __init__.py
│   ├── url_parser.py      # URL parser va validator
│   └── file_utils.py      # Fayl operatsiyalari
├── downloads/             # Yuklangan fayllar (avto yaratiladi)
└── temp/                  # Vaqtinchalik fayllar (avto yaratiladi)
```

## 🔧 O'rnatish

### 1. Tizim talablari

```bash
# Python 3.8+ o'rnatilganligini tekshiring
python3 --version

# FFmpeg o'rnatish (Linux/Ubuntu)
sudo apt update
sudo apt install -y ffmpeg

# yt-dlp uchun qo'shimcha paketlar
sudo apt install -y python3-pip python3-venv
```

### 2. Loyihani klon qilish

```bash
cd /workspace
# yoki loyiha papkasiga o'ting
cd telegram_downloader_bot
```

### 3. Virtual environment yaratish

```bash
# Virtual environment yaratish
python3 -m venv venv

# Aktivatsiya qilish
source venv/bin/activate
```

### 4. Dependencies o'rnatish

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Environment sozlamalari

```bash
# .env faylini yaratish
cp .env.example .env

# .env faylini tahrirlang va BOT_TOKEN ni kiriting
nano .env
```

`.env` fayli namunasi:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=123456789
LOG_LEVEL=INFO
```

**Bot token olish:**
1. Telegram'da [@BotFather](https://t.me/BotFather) ga murojaat qiling
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va username kiriting
4. Token olasiz - uni `.env` fayliga qo'shing

## ▶️ Ishga Tushirish

### Development rejimi

```bash
# Virtual environment aktiv bo'lishi kerak
source venv/bin/activate

# Botni ishga tushirish
python main.py
```

### Production rejimi (systemd service)

1. Service fayli yaratish:

```bash
sudo nano /etc/systemd/system/telegram-downloader.service
```

2. Quyidagi konfiguratsiyani qo'shing:

```ini
[Unit]
Description=Telegram Media Downloader Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/workspace/telegram_downloader_bot
Environment="PATH=/workspace/telegram_downloader_bot/venv/bin"
ExecStart=/workspace/telegram_downloader_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Service ni ishga tushirish:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (avtomatik ishga tushishi uchun)
sudo systemctl enable telegram-downloader

# Start service
sudo systemctl start telegram-downloader

# Status tekshirish
sudo systemctl status telegram-downloader

# Loglarni ko'rish
sudo journalctl -u telegram-downloader -f
```

## 🎯 Foydalanish

1. Botni Telegram'da topib `/start` bosing
2. Instagram, TikTok yoki YouTube havolasini yuboring
3. Bot media yuklab oladi va sizga yuboradi

**Misol havolalar:**
- Instagram: `https://instagram.com/reel/ABC123`
- TikTok: `https://tiktok.com/@user/video/123456`
- YouTube: `https://youtube.com/shorts/ABC123`

## ⚙️ Konfiguratsiya

| O'zgaruvchi | Tavsif | Default |
|------------|--------|---------|
| `BOT_TOKEN` | Telegram Bot Token | - |
| `ADMIN_ID` | Admin ID (loglar uchun) | 0 |
| `LOG_LEVEL` | Log darajasi | INFO |

## 🔒 Cheklovlar

- **Maksimal fayl hajmi**: 50 MB (Telegram Bot API limiti)
- **Karusel elementlari**: Maksimum 20 ta
- **Timeout**: 60 soniya

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'aiogram'"

```bash
# Virtual environment aktiv emas
source venv/bin/activate
pip install -r requirements.txt
```

### "yt-dlp download failed"

```bash
# yt-dlp ni yangilash
pip install --upgrade yt-dlp

# FFmpeg o'rnatilganligini tekshiring
ffmpeg -version
```

### "File size too large"

Fayl hajmi 50MB dan oshmasligi kerak. Katta videolar uchun ogohlantirish beriladi.

### "Private profile" yoki "Video unavailable"

- Profil yopiq (private) bo'lsa yuklab bo'lmaydi
- Video o'chirilgan bo'lsa ham yuklab bo'lmaydi

## 📝 Logs

Loglarni ko'rish:

```bash
# Agar systemd service ishlatilsa
sudo journalctl -u telegram-downloader -f

# Yoki to'g'ridan-to'g'ri
tail -f logs/bot.log  # agar logging faylga yo'naltirilsa
```

## 🛡️ Xavfsizlik

- `.env` faylini git-ga qo'shmang
- Bot tokenini maxfiy saqlang
- Production'da HTTPS webhook ishlating
- Rate limiting qo'shing (kerak bo'lsa)

## 📄 Litsenziya

MIT License - Erkin foydalanish mumkin.

## 👨‍💻 Muallif

Senior Backend & Telegram Bot Developer

---

**Qo'shimcha savollar uchun:** Documentation'larni o'qing yoki kodda izohlar bilan tanishing.
