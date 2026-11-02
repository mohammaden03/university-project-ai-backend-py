import re
import unicodedata
from typing import Optional


class PersianArabicNormalizer:
    """
    Dedicated Persian and Arabic text normalizer designed for historical manuscript search.
    Preserves original text for historical fidelity while providing normalized forms
    for lexical, trigram, and semantic indexing.
    """

    # Arabic and Persian character mappings
    CHAR_MAP = {
        # Kaf variants
        "\u0643": "\u06a9",  # Arabic Kaf ك -> Persian Keheh ک
        "\u06aa": "\u06a9",  # Swash Kaf
        # Yeh variants
        "\u064a": "\u06cc",  # Arabic Yeh ي -> Persian Yeh ی
        "\u0649": "\u06cc",  # Alef Maksura ى -> Persian Yeh ی
        "\u0626": "\u06cc",  # Yeh with Hamza above ئ -> Persian Yeh ی
        "\u06cd": "\u06cc",  # Yeh with Tail
        "\u06ce": "\u06cc",  # Small Yeh
        "\u06d0": "\u06cc",  # E
        "\u06d1": "\u06cc",  # Yeh with three dots
        # Teh Marbuta
        "\u0629": "\u0647",  # Teh Marbuta ة -> Heh ه
        # Alef variants
        "\u0622": "\u0627",  # Alef with Madda آ -> Alef ا
        "\u0623": "\u0627",  # Alef with Hamza Above أ -> Alef ا
        "\u0625": "\u0627",  # Alef with Hamza Below إ -> Alef ا
        "\u0671": "\u0627",  # Alef Wasla ٱ -> Alef ا
        # Waw variants
        "\u0624": "\u0648",  # Waw with Hamza ؤ -> Waw و
    }

    # Arabic and Persian numerals to ASCII
    DIGIT_MAP = {
        "\u0660": "0", "\u0661": "1", "\u0662": "2", "\u0663": "3", "\u0664": "4",
        "\u0665": "5", "\u0666": "6", "\u0667": "7", "\u0668": "8", "\u0669": "9",
        "\u06f0": "0", "\u06f1": "1", "\u06f2": "2", "\u06f3": "3", "\u06f4": "4",
        "\u06f5": "5", "\u06f6": "6", "\u06f7": "7", "\u06f8": "8", "\u06f9": "9",
    }

    # Diacritics (Harakat / Tashkeel) regex
    # Fatha, Damma, Kasra, Fathatan, Dammatan, Kasratan, Shadda, Sukun, etc.
    DIACRITICS_REGEX = re.compile(
        r"[\u064B-\u0652\u0656-\u065F\u0670\u06D6-\u06ED]"
    )

    # Tatweel / Kashida (ـ)
    TATWEEL_REGEX = re.compile(r"\u0640+")

    # Repeated whitespace
    WHITESPACE_REGEX = re.compile(r"\s+")

    # Punctuation for search normalization
    PUNCT_REGEX = re.compile(r"[\.,،؛:\(\)\[\]\{\}\<\>«»\"'!\?؟\-\—\/\\_]")

    @classmethod
    def normalize_for_search(
        cls,
        text: Optional[str],
        remove_diacritics: bool = True,
        remove_tatweel: bool = True,
        unify_letters: bool = True,
        convert_digits: bool = True,
        remove_punctuation: bool = False,
    ) -> str:
        """
        Normalize text specifically for search matching and indexing.
        Does not mutate the caller's text.
        """
        if not text:
            return ""

        # 1. Unicode Normalization Form C
        res = unicodedata.normalize("NFC", text)

        # 2. Remove Tatweel / Kashida
        if remove_tatweel:
            res = cls.TATWEEL_REGEX.sub("", res)

        # 3. Remove Diacritics
        if remove_diacritics:
            res = cls.DIACRITICS_REGEX.sub("", res)

        # 4. Unify Kaf, Yeh, Alef, Teh Marbuta
        if unify_letters:
            chars = [cls.CHAR_MAP.get(ch, ch) for ch in res]
            res = "".join(chars)

        # 5. Convert Arabic & Persian Digits to ASCII digits
        if convert_digits:
            chars = [cls.DIGIT_MAP.get(ch, ch) for ch in res]
            res = "".join(chars)

        # 6. Optional punctuation stripping
        if remove_punctuation:
            res = cls.PUNCT_REGEX.sub(" ", res)

        # 7. Collapse whitespace & trim
        res = cls.WHITESPACE_REGEX.sub(" ", res).strip()

        return res

    @classmethod
    def normalize_for_display(cls, text: Optional[str]) -> str:
        """
        Gentle normalization that keeps diacritics and original letters intact,
        only fixing unicode composition and excessive whitespace.
        """
        if not text:
            return ""
        res = unicodedata.normalize("NFC", text)
        res = cls.WHITESPACE_REGEX.sub(" ", res).strip()
        return res


def normalize_text(text: Optional[str], remove_diacritics: bool = True) -> str:
    """Convenience functional wrapper."""
    return PersianArabicNormalizer.normalize_for_search(
        text, remove_diacritics=remove_diacritics
    )
