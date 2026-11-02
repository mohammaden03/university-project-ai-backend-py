import pytest
from app.utils.text_normalization import PersianArabicNormalizer, normalize_text


def test_arabic_persian_letter_unification():
    # Arabic Kaf and Yeh variants
    arabic_text = "كتاب الحاوي في الطب ليحيى بن زكريا"
    normalized = normalize_text(arabic_text)
    assert "کتاب" in normalized  # Arabic ك replaced by Persian ک
    assert "الحاوی" in normalized  # Arabic ي replaced by Persian ی
    assert "فی" in normalized
    assert "یحیی" in normalized  # Alef Maksura replaced


def test_tatweel_removal():
    kashida_text = "بــــسم الله الــــرحمـن الرحــــیم"
    normalized = normalize_text(kashida_text)
    assert "ـ" not in normalized
    assert normalized == "بسم الله الرحمن الرحیم"


def test_diacritics_tashkeel_removal():
    vocalized_text = "قَانُونٌ فِي الطِّبِّ لِلشَّيْخِ الرَّئِيسِ"
    normalized = normalize_text(vocalized_text)
    assert "َ" not in normalized
    assert "ِ" not in normalized
    assert "ُ" not in normalized
    assert "ّ" not in normalized
    assert "ْ" not in normalized
    assert "قانون فی الطب للشیخ الرئیس" in normalized


def test_alef_and_digit_normalization():
    text_with_alef = "أبو عليّ إبن سينا ولد عام ۳۷۰ هجرية"
    normalized = normalize_text(text_with_alef)
    assert "ابو" in normalized
    assert "ابن" in normalized
    assert "370" in normalized
    assert "هجریه" in normalized  # Teh Marbuta unified
