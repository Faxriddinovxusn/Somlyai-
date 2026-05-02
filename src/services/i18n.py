import json
import os
from pathlib import Path

LOCALES_DIR = Path(__file__).parent.parent / "locales"

_translations = {}

def load_locales():
    global _translations
    for lang in ["uz", "ru", "en"]:
        file_path = LOCALES_DIR / f"{lang}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                _translations[lang] = json.load(f)
        else:
            _translations[lang] = {}

load_locales()

def t(lang: str, key: str, **kwargs) -> str:
    """
    Get translation for a given language and key.
    Replaces kwargs in the string using format().
    """
    if not lang:
        lang = "uz"
    
    lang_dict = _translations.get(lang, _translations.get("uz", {}))
    text = lang_dict.get(key)
    
    # Fallback to UZ if key missing in chosen lang
    if not text and lang != "uz":
        text = _translations.get("uz", {}).get(key)
        
    if not text:
        return key  # fallback to key name
        
    try:
        return text.format(**kwargs)
    except Exception:
        return text
