import streamlit as st
import requests
import re
import pandas as pd

st.title("🔥 Email Scraper Tool")

domains = st.text_area("Enter domains (one per line)")

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

def get_emails(url):
    try:
        r = requests.get(url, timeout=10)
        return list(set(re.findall(EMAIL_REGEX, r.text)))
    except:
        return []

if st.button("Scrape"):
    results = []

    for d in domains.split("\n"):
        d = d.strip()
        if not d:
            continue

        if not d.startswith("http"):
            d = "https://" + d

        emails = get_emails(d)

        if emails:
            for e in emails:
                results.append([d, e])
        else:
            results.append([d, "101"])

    df = pd.DataFrame(results, columns=["Website", "Email"])

    st.dataframe(df)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "emails.csv"
    )
