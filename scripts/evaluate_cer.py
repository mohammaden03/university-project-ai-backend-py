"""
Evaluation metrics utility for Character Error Rate (CER) and Word Error Rate (WER)
Calculates normalized Levenshtein edit distance between ground truth and HTR prediction.
"""
from typing import List, Tuple
from app.utils.text_normalization import PersianArabicNormalizer


def levenshtein_distance(seq1: List[str], seq2: List[str]) -> int:
    """Calculates Levenshtein edit distance between two token sequences."""
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = [[0] * size_y for _ in range(size_x)]

    for x in range(size_x):
        matrix[x][0] = x
    for y in range(size_y):
        matrix[0][y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x - 1] == seq2[y - 1]:
                matrix[x][y] = matrix[x - 1][y - 1]
            else:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,      # deletion
                    matrix[x][y - 1] + 1,      # insertion
                    matrix[x - 1][y - 1] + 1,  # substitution
                )
    return matrix[size_x - 1][size_y - 1]


def compute_cer(reference: str, hypothesis: str, normalize: bool = True) -> float:
    """
    Character Error Rate = Levenshtein(ref_chars, hyp_chars) / len(ref_chars)
    """
    if normalize:
        ref = PersianArabicNormalizer.normalize_for_search(reference)
        hyp = PersianArabicNormalizer.normalize_for_search(hypothesis)
    else:
        ref = reference
        hyp = hypothesis

    ref_chars = list(ref)
    hyp_chars = list(hyp)

    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0

    edit_dist = levenshtein_distance(ref_chars, hyp_chars)
    return round(edit_dist / float(len(ref_chars)), 4)


def compute_wer(reference: str, hypothesis: str, normalize: bool = True) -> float:
    """
    Word Error Rate = Levenshtein(ref_words, hyp_words) / len(ref_words)
    """
    if normalize:
        ref = PersianArabicNormalizer.normalize_for_search(reference)
        hyp = PersianArabicNormalizer.normalize_for_search(hypothesis)
    else:
        ref = reference
        hyp = hypothesis

    ref_words = ref.split()
    hyp_words = hyp.split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    edit_dist = levenshtein_distance(ref_words, hyp_words)
    return round(edit_dist / float(len(ref_words)), 4)


def evaluate_batch(references: List[str], hypotheses: List[str]) -> Tuple[float, float]:
    """Computes corpus-level CER and WER across test dataset."""
    total_ref_chars = 0
    total_char_edits = 0
    total_ref_words = 0
    total_word_edits = 0

    for ref, hyp in zip(references, hypotheses):
        norm_ref = PersianArabicNormalizer.normalize_for_search(ref)
        norm_hyp = PersianArabicNormalizer.normalize_for_search(hyp)

        ref_chars = list(norm_ref)
        hyp_chars = list(norm_hyp)
        total_ref_chars += len(ref_chars)
        total_char_edits += levenshtein_distance(ref_chars, hyp_chars)

        ref_words = norm_ref.split()
        hyp_words = norm_hyp.split()
        total_ref_words += len(ref_words)
        total_word_edits += levenshtein_distance(ref_words, hyp_words)

    mean_cer = round(total_char_edits / max(1, total_ref_chars), 4)
    mean_wer = round(total_word_edits / max(1, total_ref_words), 4)
    return mean_cer, mean_wer


if __name__ == "__main__":
    ref = "بسم الله الرحمن الرحیم شیخ الرئیس ابو علی سینا"
    hyp = "بسم الله الرحمن الرحیم شخ الرئیس ابو علی سنا"
    print(f"Sample CER: {compute_cer(ref, hyp) * 100:.2f}%")
    print(f"Sample WER: {compute_wer(ref, hyp) * 100:.2f}%")
