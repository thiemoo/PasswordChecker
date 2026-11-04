import math
import re
import string

COMMON_PATTERNS = ["1234", "abcd", "qwertz", "qwerty",
                   "passwort", "password", "admin", "hallo"]


def check_length(pw: str) -> int:
    """Bis zu 30 Punkte: 2 pro Zeichen, ab 15 Zeichen voll."""
    return min(len(pw) * 2, 30)


def check_char_classes(pw: str) -> dict:
    return {
        "klein": any(c.islower() for c in pw),
        "gross": any(c.isupper() for c in pw),
        "zahl": any(c.isdigit() for c in pw),
        "sonder": any(c in string.punctuation for c in pw),
    }


def calc_entropy(pw: str) -> float:
    classes = check_char_classes(pw)
    pool = 0
    if classes["klein"]:
        pool += 26
    if classes["gross"]:
        pool += 26
    if classes["zahl"]:
        pool += 10
    if classes["sonder"]:
        pool += len(string.punctuation)  # 32 Zeichen
    if pool == 0:
        return 0.0
    return len(pw) * math.log2(pool)


def find_patterns(pw: str) -> list[str]:
    problems = []
    lower = pw.lower()
    for p in COMMON_PATTERNS:
        if p in lower:
            problems.append(f"Enthält ein bekanntes Muster: '{p}'")
    if re.search(r"(.)\1{2,}", pw):
        problems.append("Enthält Wiederholungen wie 'aaa'")
    if re.fullmatch(r"\d+", pw):
        problems.append("Besteht nur aus Zahlen")
    if re.search(r"(19|20)\d{2}", pw):
        problems.append("Enthält eine Jahreszahl")
    return problems
