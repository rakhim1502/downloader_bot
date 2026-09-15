#!/bin/bash

# ============================================
# Telegram Downloader Bot - O'rnatish Scripti
# Linux/Ubuntu server uchun
# ============================================

set -e  # Xatolik bo'lsa to'xtash

echo "🚀 Telegram Downloader Bot - O'rnatish boshlandi..."

# Rangli output uchun
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Tizim yangilash
echo -e "${YELLOW}[1/6] Tizim yangilanmoqda...${NC}"
sudo apt update -y

# 2. Kerakli paketlarni o'rnatish
echo -e "${YELLOW}[2/6] Kerakli paketlar o'rnatilmoqda...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    curl

# 3. Python versiyasini tekshirish
echo -e "${YELLOW}[3/6] Python versiyasi tekshirilmoqda...${NC}"
python3 --version || {
    echo -e "${RED}❌ Python 3 o'rnatilmagan!${NC}"
    exit 1
}

# 4. Virtual environment yaratish
echo -e "${YELLOW}[4/6] Virtual environment yaratilmoqda...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment yaratildi${NC}"
else
    echo -e "${GREEN}✅ Virtual environment allaqachon mavjud${NC}"
fi

# 5. Dependencies o'rnatish
echo -e "${YELLOW}[5/6] Python dependencies o'rnatilmoqda...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies o'rnatildi${NC}"

# 6. .env faylini sozlash
echo -e "${YELLOW}[6/6] Environment fayli sozlanmoqda...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env fayli yaratildi${NC}"
    echo -e "${YELLOW}⚠️  DIQQAT: .env faylini tahrirlang va BOT_TOKEN ni kiriting!${NC}"
    echo -e "${YELLOW}   nano .env${NC}"
else
    echo -e "${GREEN}✅ .env fayli allaqachon mavjud${NC}"
fi

# Papkalarni yaratish
echo -e "${YELLOW}Papka yaratilmoqda...${NC}"
mkdir -p downloads temp
echo -e "${GREEN}✅ Papkalar tayyor${NC}"

# Yakuniy xabar
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ O'rnatish muvaffaqiyatli yakunlandi!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Keyingi qadamlar:${NC}"
echo "1. .env faylini tahrirlang va BOT_TOKEN ni kiriting:"
echo -e "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Botni ishga tushiring:"
echo -e "   ${YELLOW}source venv/bin/activate && python main.py${NC}"
echo ""
echo "3. Yoki systemd service sifatida ishga tushiring:"
echo -e "   ${YELLOW}sudo systemctl enable telegram-downloader && sudo systemctl start telegram-downloader${NC}"
echo ""
echo -e "${GREEN}Muvaffaqiyat tilaymiz! 🎉${NC}"
