import hashlib

import requests

API_URL = "https://api.pwnedpasswords.com/range/"


def is_pwned(pw: str) -> int:
    """Gibt zurück, wie oft das Passwort in Leaks vorkam (0 = nie)."""
    sha1 = hashlib.sha1(pw.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    response = requests.get(
        API_URL + prefix,
        headers={"User-Agent": "passwort-checker-lernprojekt",
                 "Add-Padding": "true"},
        timeout=5,
    )
    response.raise_for_status()

    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return int(count)
    return 0
