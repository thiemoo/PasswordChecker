from getpass import getpass

from checker import rate_password

result = rate_password(getpass("Passwort: "))
print(f"Score: {result['score']}/100 ({result['level']})")
print(f"Entropie: {result['entropy']} Bit")
for p in result["problems"]:
    print("  !", p)
for t in result["tips"]:
    print("  ->", t)
