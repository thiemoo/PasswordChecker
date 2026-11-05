# Passwort-Checker

Wie gut ist mein Passwort eigentlich? Und taucht es vielleicht schon in irgendeinem Datenleak auf?
Genau das beantwortet dieses kleine Tool. Ich habe es gebaut, um mich mit Hashing, APIs und einem
sauberen Python-Projekt-Setup auseinanderzusetzen.

<!-- Screenshot hier einfügen -->

## Was es kann

Du gibst ein Passwort ein und bekommst:

- einen **Score von 0 bis 100** mit Einstufung (schwach / mittel / stark)
- die **Entropie** in Bit, also grob, wie schwer das Passwort zu erraten ist
- Hinweise auf **typische Schwächen** wie „1234“, „qwertz“, „aaa“ oder Jahreszahlen
- einen **Leak-Check** über [Have I Been Pwned](https://haveibeenpwned.com/Passwords)
- konkrete **Tipps**, was du verbessern kannst

Es gibt drei Varianten: ein Fenster-Programm (auch als `.exe`), eine Version für die Kommandozeile
und eine Weboberfläche mit Streamlit.

## Warum das Passwort sicher bleibt

Das war mir beim Bauen am wichtigsten: Ein Passwort-Checker, der dein Passwort irgendwohin schickt,
wäre ziemlich absurd. Deshalb wird das Passwort **nie gespeichert und nie vollständig verschickt,
nicht einmal als Hash**.

Möglich macht das ein Verfahren namens **k-Anonymity**:

1. Das Passwort wird lokal mit SHA-1 gehasht, z. B. `5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8`.
2. Nur die ersten 5 Zeichen (`5BAA6`) gehen an die API.
3. Die API schickt alle bekannten Hashes mit diesem Anfang zurück, meistens ein paar Hundert.
4. Ob der Rest des eigenen Hashes dabei ist, prüft das Programm auf deinem Rechner.

Die API erfährt also nur, dass irgendein Passwort aus einer Gruppe von Hunderten angefragt wurde.
Zusätzlich sorgt der Header `Add-Padding` dafür, dass die Antwort mit Fake-Einträgen aufgefüllt
wird. So lässt sich nicht einmal an der Größe der Antwort ablesen, welcher Prefix gefragt war.

## Wie der Score entsteht

| Was | Punkte |
|---|---|
| Länge (2 pro Zeichen) | bis zu 30 |
| Zeichenklassen: klein, groß, Zahl, Sonderzeichen | je 10 |
| Entropie | bis zu 30 |
| Bekanntes Muster gefunden | −15 pro Muster |
| Passwort ist geleakt | maximal 10, egal wie lang |

Die Entropie berechne ich mit `E = L · log2(N)`, wobei `L` die Länge ist und `N` die Anzahl der
möglichen Zeichen. Als Faustregel gilt: unter 40 Bit ist schwach, ab 60 Bit gut, ab 80 Bit sehr stark.

Ehrlich gesagt ist das eine Vereinfachung. `P@ssw0rd2024` sieht für die Formel ganz ordentlich aus,
ist in der Praxis aber schnell geknackt. Genau dafür gibt es die Muster-Erkennung und den Leak-Check.

## Ausprobieren

**Einfach so:** `Passwort-Checker.exe` herunterladen (unter Releases) und doppelklicken.
Windows warnt eventuell, weil die Datei nicht signiert ist. Dann auf
„Weitere Informationen → Trotzdem ausführen“ klicken.

**Aus dem Code:** Du brauchst Python 3.10 oder neuer.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Danach:

```
python gui.py            # Fenster-Programm
python cli.py            # Kommandozeile (Eingabe bleibt unsichtbar)
streamlit run app.py     # im Browser
pytest                   # Tests laufen lassen
```

Die `.exe` selbst bauen:

```
pyinstaller --noconfirm --onefile --windowed --name Passwort-Checker gui.py
```

Sie landet dann in `dist\`.

## Aufbau

```
checker/
  strength.py   Länge, Zeichenklassen, Entropie, Muster
  pwned.py      Leak-Check über Have I Been Pwned
  __init__.py   rate_password() fasst alles zusammen
gui.py          Fenster-Programm (tkinter)
cli.py          Kommandozeile
app.py          Streamlit-Oberfläche
tests/          pytest-Tests
```

Eine Sache, die ich beim Fenster-Programm gelernt habe: Der Leak-Check läuft in einem eigenen
Thread, damit das Fenster während der Anfrage nicht einfriert. tkinter darf aber nur aus dem
Haupt-Thread verändert werden. Deshalb legt der Hintergrund-Thread sein Ergebnis in eine Queue,
und das Fenster holt es von dort ab.
