"""
Xorijiy valyutalar kursini Markaziy Bank (CBU) API'sidan olish xizmati.
"""
import logging
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

# Kesh (Xotirada saqlash)
_cached_rates = {}
_last_update_time = None

async def fetch_and_cache_cbu_rates():
    """CBU API'sidan so'nggi kurslarni oladi va keshlaydi."""
    global _cached_rates, _last_update_time
    url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Convert to a dict mapped by currency code (e.g., 'USD', 'EUR')
                    new_rates = {}
                    for item in data:
                        code = item.get("Ccy")
                        rate = item.get("Rate")
                        if code and rate:
                            try:
                                new_rates[code] = float(rate)
                            except ValueError:
                                pass
                                
                    if new_rates:
                        _cached_rates = new_rates
                        _last_update_time = datetime.utcnow()
                        logger.info(f"CBU rates successfully updated. USD: {_cached_rates.get('USD')}")
                        return True
                else:
                    logger.error(f"Failed to fetch CBU rates. Status: {response.status}")
    except Exception as e:
        logger.error(f"Error fetching CBU rates: {e}")
        
    return False

def get_exchange_rates():
    """Keshdagi valyuta kurslarini va yangilangan vaqtni qaytaradi."""
    return {
        "rates": _cached_rates,
        "last_updated": _last_update_time.isoformat() if _last_update_time else None
    }
