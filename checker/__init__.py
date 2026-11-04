import requests

from .strength import check_length, check_char_classes, calc_entropy, find_patterns
from .pwned import is_pwned


def rate_password(pw: str) -> dict:
    classes = check_char_classes(pw)
    entropy = calc_entropy(pw)
    problems = find_patterns(pw)

    score = check_length(pw)
    score += sum(classes.values()) * 10
    score += min(entropy / 80 * 30, 30)
    score -= len(problems) * 15

    try:
        leaks = is_pwned(pw)
    except requests.RequestException:
        leaks = None  # offline, Prüfung übersprungen

    if leaks:
        score = min(score, 10)
        problems.append(f"Wurde {leaks:,}-mal in Datenleaks gefunden!")

    score = max(0, min(100, round(score)))
    level = "schwach" if score < 40 else "mittel" if score < 70 else "stark"

    tips = []
    if len(pw) < 12:
        tips.append("Mindestens 12 Zeichen verwenden")
    for name, ok in classes.items():
        if not ok:
            tips.append(f"Zeichenklasse ergänzen: {name}")

    return {"score": score, "level": level, "entropy": round(entropy, 1),
            "leaks": leaks, "problems": problems, "tips": tips}
