import os
import aiohttp
import logging

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

async def download_instagram_media(url: str):
    """RapidAPI orqali Instagram video/rasm URL'ini olish."""
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
                    # API beradigan javob tuzilmasiga qarab media URL olinadi
                    download_url = data.get("download_url") or data.get("url")
                    return download_url
                else:
                    logging.error(f"RapidAPI xatosi: status {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Instagram yuklashda xatolik: {e}")
        return None