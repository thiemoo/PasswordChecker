"""Fenster-Version des Passwort-Checkers (tkinter)."""
import queue
import threading
import tkinter as tk
from tkinter import ttk

from checker import rate_password

LEVEL_COLORS = {"schwach": "#d64545", "mittel": "#e0a030", "stark": "#3a9a5b"}


class CheckerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.results: queue.Queue = queue.Queue()
        root.title("Passwort-Checker")
        root.geometry("460x420")
        root.minsize(380, 360)

        style = ttk.Style(root)
        style.theme_use("clam")
        for level, color in LEVEL_COLORS.items():
            style.configure(f"{level}.Horizontal.TProgressbar",
                            background=color, troughcolor="#e6e6e6")

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Passwort eingeben:").pack(anchor="w")

        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(4, 0))
        self.pw = tk.StringVar()
        self.entry = ttk.Entry(row, textvariable=self.pw, show="•")
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda _e: self.check())
        self.entry.focus()
        self.button = ttk.Button(row, text="Prüfen", command=self.check)
        self.button.pack(side="left", padx=(8, 0))

        self.show = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Passwort anzeigen", variable=self.show,
                        command=self.toggle_show).pack(anchor="w", pady=(6, 12))

        self.bar = ttk.Progressbar(frame, maximum=100)
        self.bar.pack(fill="x")
        self.score_label = ttk.Label(frame, text="", font=("Segoe UI", 12, "bold"))
        self.score_label.pack(anchor="w", pady=(6, 0))
        self.entropy_label = ttk.Label(frame, text="")
        self.entropy_label.pack(anchor="w")
        self.leak_label = ttk.Label(frame, text="")
        self.leak_label.pack(anchor="w", pady=(4, 8))

        self.details = tk.Text(frame, height=8, wrap="word", relief="flat",
                               background=root.cget("background"),
                               font=("Segoe UI", 10))
        self.details.pack(fill="both", expand=True)
        self.details.configure(state="disabled")

    def toggle_show(self):
        self.entry.configure(show="" if self.show.get() else "•")

    def check(self):
        pw = self.pw.get()
        if not pw:
            return
        self.button.configure(state="disabled")
        self.score_label.configure(text="Prüfe …", foreground="")
        # Netzwerkanfrage im Hintergrund, damit das Fenster nicht einfriert.
        # tkinter darf nur aus dem Haupt-Thread angefasst werden, deshalb
        # legt der Worker das Ergebnis in eine Queue, die _poll() abholt.
        threading.Thread(target=lambda: self.results.put(rate_password(pw)),
                         daemon=True).start()
        self._poll()

    def _poll(self):
        try:
            result = self.results.get_nowait()
        except queue.Empty:
            self.root.after(50, self._poll)
        else:
            self.show_result(result)

    def show_result(self, r: dict):
        self.button.configure(state="normal")
        color = LEVEL_COLORS[r["level"]]
        self.bar.configure(value=r["score"],
                           style=f"{r['level']}.Horizontal.TProgressbar")
        self.score_label.configure(text=f"{r['score']}/100 – {r['level']}",
                                   foreground=color)
        self.entropy_label.configure(text=f"Entropie: {r['entropy']} Bit")

        if r["leaks"]:
            self.leak_label.configure(
                text=f"In {r['leaks']:,} Leaks gefunden. Nicht verwenden!",
                foreground=LEVEL_COLORS["schwach"])
        elif r["leaks"] == 0:
            self.leak_label.configure(text="In keinem bekannten Leak gefunden.",
                                      foreground=LEVEL_COLORS["stark"])
        else:
            self.leak_label.configure(text="Leak-Check nicht möglich (offline?)",
                                      foreground=LEVEL_COLORS["mittel"])

        lines = [f"⚠ {p}" for p in r["problems"]] + [f"→ {t}" for t in r["tips"]]
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", "\n".join(lines))
        self.details.configure(state="disabled")


def main():
    root = tk.Tk()
    CheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
