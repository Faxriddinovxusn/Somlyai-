"""
Test script for AI categorization system.
Tests the new translate_category_name() and detect_category_for_transaction() methods.

Usage:
    python test_ai_categorization.py
"""

import asyncio
import sys
sys.path.insert(0, '/path/to/somly-ai')

from src.services.groq_service import groq_service
from src.categories import SYSTEM_CATEGORIES

# Sample custom categories for testing
SAMPLE_CUSTOM_CATEGORIES = [
    {"name": "Shaxsiy", "emoji": "👤", "type": "chiqim"},
    {"name": "Safarish", "emoji": "🛵", "type": "chiqim"},
]

async def test_translate_category_name():
    """Test English → Uzbek category name translation."""
    print("=" * 60)
    print("TEST 1: Category Name Translation (English → Uzbek)")
    print("=" * 60)
    
    test_cases = [
        "slap",
        "gym",
        "coffee",
        "transport",
        "electricity",
        "internet",
        "pharmacy",
        "groceries",
    ]
    
    for english_name in test_cases:
        uzbek_name = await groq_service.translate_category_name(english_name)
        print(f"  {english_name:20} → {uzbek_name}")
    print()


async def test_detect_category_for_transaction():
    """Test transaction description → category detection."""
    print("=" * 60)
    print("TEST 2: Transaction Category Detection")
    print("=" * 60)
    
    test_descriptions = [
        ("Taksiga 15 ming to'ladim", "kirim/chiqim"),
        ("Restoranda ovqat sotib oldim", "chiqim"),
        ("Fitnes zalida 3 oylik obuna", "chiqim"),
        ("Dori aptekasida dori sotib oldim", "chiqim"),
        ("Oylik maosh tushdi", "kirim"),
        ("Kompyuter sotib oldim", "chiqim"),
        ("Safarish bilan uyga piksa buyurtma qildim", "chiqim"),
        ("Aziz menga 50 ming puli berdi", "kirim"),
    ]
    
    for description, expected_type in test_descriptions:
        result = await groq_service.detect_category_for_transaction(
            description=description,
            personal_categories=SAMPLE_CUSTOM_CATEGORIES,
            system_categories=SYSTEM_CATEGORIES[:20],  # Top 20 for brevity
            user_id=12345
        )
        
        print(f"\n  Description: {description}")
        print(f"  Expected type: {expected_type}")
        print(f"  → Category: {result['emoji']} {result['category']}")
        print(f"    Confidence: {result['confidence']:.2f}")


async def test_edge_cases():
    """Test edge cases and fallback behavior."""
    print("\n" + "=" * 60)
    print("TEST 3: Edge Cases & Fallback Behavior")
    print("=" * 60)
    
    edge_cases = [
        "",                    # Empty description
        "123",                 # Only numbers
        "xyz abc def",         # Random text
        "?!@#$%",             # Special characters only
    ]
    
    for description in edge_cases:
        result = await groq_service.detect_category_for_transaction(
            description=description or "(empty)",
            personal_categories=SAMPLE_CUSTOM_CATEGORIES,
            system_categories=SYSTEM_CATEGORIES[:10],
            user_id=12345
        )
        
        print(f"\n  Description: '{description}' (length: {len(description)})")
        print(f"  → Fallback: {result['emoji']} {result['category']}")
        print(f"    Confidence: {result['confidence']:.2f}")


async def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 14 + "AI CATEGORIZATION SYSTEM TEST SUITE" + " " * 10 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    try:
        await test_translate_category_name()
        await test_detect_category_for_transaction()
        await test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
