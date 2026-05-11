"""
QR Code Receipt Scanner Service.
Reads QR codes from images and fetches fiscal receipt data from fiscal.soliq.uz.

pyzbar → pyzbar2 fallback supported.
"""

import logging
import io
from urllib.parse import urlparse, parse_qs

import aiohttp
from PIL import Image
from bs4 import BeautifulSoup

# pyzbar / pyzbar2 fallback
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
except ImportError:
    try:
        from pyzbar2.pyzbar2 import decode as pyzbar_decode
    except ImportError:
        pyzbar_decode = None
        logging.getLogger(__name__).error("Neither pyzbar nor pyzbar2 is installed!")

logger = logging.getLogger(__name__)


def decode_qr_from_bytes(image_bytes: bytes) -> str | None:
    """
    Rasmdan QR kodni o'qib, URL qaytaradi.
    Topilmasa None.
    """
    if pyzbar_decode is None:
        logger.error("QR decoder not available (pyzbar/pyzbar2 not installed)")
        return None

    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB if needed (pyzbar sometimes struggles with RGBA/P)
        if img.mode not in ("L", "RGB"):
            img = img.convert("RGB")

        decoded = pyzbar_decode(img)
        if not decoded:
            return None

        # Birinchi topilgan QR kodning ma'lumotini qaytarish
        qr_data = decoded[0].data.decode("utf-8", errors="ignore")
        return qr_data
    except Exception as e:
        logger.error(f"QR decode error: {e}")
        return None


def is_fiscal_url(url: str) -> bool:
    """URL fiscal.soliq.uz ga tegishli ekanligini tekshirish."""
    try:
        parsed = urlparse(url)
        return "fiscal.soliq.uz" in parsed.netloc or "soliq.uz" in parsed.netloc
    except Exception:
        return False


def extract_fiscal_params(url: str) -> dict:
    """
    Fiscal URL dan parametrlarni ajratib olish.
    Qaytaradi: {tin, time, sum, fiscalSign, ...}
    """
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        result = {}
        for key in ["t", "s", "fn", "i", "fp", "tin", "time", "sum", "fiscalSign"]:
            if key in params:
                result[key] = params[key][0]
        return result
    except Exception as e:
        logger.error(f"Fiscal params extract error: {e}")
        return {}


async def fetch_fiscal_receipt(qr_url: str) -> dict:
    """
    fiscal.soliq.uz dan chek ma'lumotlarini olish.
    
    Returns:
    {
        "success": True/False,
        "shop_name": "Korzinka",
        "date": "25.04.2026 14:32",
        "total": 87500,
        "items": [{"name": "...", "price": 8500, "qty": 1}, ...],
        "qqs": 0,
        "raw_url": "...",
        "error": None
    }
    """
    result = {
        "success": False,
        "shop_name": None,
        "date": None,
        "total": 0,
        "items": [],
        "qqs": 0,
        "raw_url": qr_url,
        "error": None
    }

    # URL dan parametrlar
    params = extract_fiscal_params(qr_url)

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.get(qr_url, ssl=False) as resp:
                if resp.status != 200:
                    result["error"] = f"HTTP {resp.status}"
                    # Fallback: URL dagi sum parametridan
                    if "sum" in params or "s" in params:
                        raw_sum = params.get("sum", params.get("s", "0"))
                        try:
                            result["total"] = int(float(raw_sum))
                            result["success"] = True
                        except ValueError:
                            pass
                    return result

                html = await resp.text()

    except aiohttp.ClientError as e:
        logger.error(f"Fiscal fetch error: {e}")
        result["error"] = "connection_error"
        # Fallback: URL parametrlari
        if "sum" in params or "s" in params:
            raw_sum = params.get("sum", params.get("s", "0"))
            try:
                result["total"] = int(float(raw_sum))
                result["success"] = True
            except ValueError:
                pass
        return result
    except Exception as e:
        logger.error(f"Fiscal fetch unexpected error: {e}")
        result["error"] = str(e)
        return result

    # HTML ni parse qilish
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Do'kon nomi
        shop_el = soup.select_one(".company-name, .receipt-company, h2, .shop-name")
        if shop_el:
            result["shop_name"] = shop_el.get_text(strip=True)

        # Sana
        date_el = soup.select_one(".receipt-date, .date, .check-date")
        if date_el:
            result["date"] = date_el.get_text(strip=True)
        elif "time" in params:
            result["date"] = params["time"]

        # Mahsulotlar
        items = []
        rows = soup.select("table tr, .item-row, .product-row, .receipt-item")
        for row in rows:
            cols = row.select("td, .item-name, .item-price")
            if len(cols) >= 2:
                name = cols[0].get_text(strip=True)
                price_text = cols[-1].get_text(strip=True)
                # Raqamlarni ajratib olish
                price_clean = "".join(c for c in price_text if c.isdigit() or c == ".")
                try:
                    price = int(float(price_clean)) if price_clean else 0
                except ValueError:
                    price = 0
                if name and price > 0:
                    items.append({"name": name, "price": price, "qty": 1})
        result["items"] = items

        # Jami summa
        total_el = soup.select_one(".total, .receipt-total, .sum, .total-sum")
        if total_el:
            total_text = total_el.get_text(strip=True)
            total_clean = "".join(c for c in total_text if c.isdigit() or c == ".")
            try:
                result["total"] = int(float(total_clean)) if total_clean else 0
            except ValueError:
                pass

        # Fallback: URL dan sum
        if result["total"] == 0 and ("sum" in params or "s" in params):
            raw_sum = params.get("sum", params.get("s", "0"))
            try:
                result["total"] = int(float(raw_sum))
            except ValueError:
                pass

        # QQS
        qqs_el = soup.select_one(".nds, .vat, .qqs")
        if qqs_el:
            qqs_text = qqs_el.get_text(strip=True)
            qqs_clean = "".join(c for c in qqs_text if c.isdigit() or c == ".")
            try:
                result["qqs"] = int(float(qqs_clean)) if qqs_clean else 0
            except ValueError:
                pass

        result["success"] = True

    except Exception as e:
        logger.error(f"Fiscal parse error: {e}")
        result["error"] = "parse_error"
        # Fallback: URL parametrlari
        if "sum" in params or "s" in params:
            raw_sum = params.get("sum", params.get("s", "0"))
            try:
                result["total"] = int(float(raw_sum))
                result["success"] = True
            except ValueError:
                pass

    return result


def format_receipt_message(receipt: dict) -> str:
    """Chek ma'lumotlarini foydalanuvchiga ko'rsatish uchun formatlash."""
    lines = ["🧾 <b>Chek ma'lumotlari:</b>\n"]

    if receipt.get("shop_name"):
        lines.append(f"🏪 Do'kon: <b>{receipt['shop_name']}</b>")

    if receipt.get("date"):
        lines.append(f"📅 Sana: {receipt['date']}")

    if receipt.get("total"):
        formatted_total = f"{receipt['total']:,}".replace(",", " ")
        lines.append(f"💵 Jami: <b>{formatted_total} UZS</b>")

    if receipt.get("items"):
        lines.append("\n<b>Mahsulotlar:</b>")
        shown = receipt["items"][:8]
        for item in shown:
            price_fmt = f"{item['price']:,}".replace(",", " ")
            lines.append(f"  • {item['name']} — {price_fmt} UZS")
        remaining = len(receipt["items"]) - len(shown)
        if remaining > 0:
            lines.append(f"  • ... va yana {remaining} ta")

    if receipt.get("qqs") and receipt["qqs"] > 0:
        qqs_fmt = f"{receipt['qqs']:,}".replace(",", " ")
        lines.append(f"\n💰 QQS: {qqs_fmt} UZS")

    lines.append(f"\nKategoriya: 🍔 Oziq-ovqat")

    return "\n".join(lines)
