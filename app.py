import streamlit as st

from checker import rate_password

st.title("Passwort-Checker")
pw = st.text_input("Passwort eingeben", type="password")

if pw:
    r = rate_password(pw)
    st.progress(r["score"] / 100, text=f"{r['score']}/100 – {r['level']}")
    st.metric("Entropie", f"{r['entropy']} Bit")

    if r["leaks"]:
        st.error(f"In {r['leaks']:,} Leaks gefunden. Nicht verwenden!")
    elif r["leaks"] == 0:
        st.success("In keinem bekannten Leak gefunden.")
    else:
        st.warning("Leak-Check nicht möglich (offline?)")

    for p in r["problems"]:
        st.write("⚠️", p)
    for t in r["tips"]:
        st.write("💡", t)
