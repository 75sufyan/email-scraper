import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= CONFIG =================
st.set_page_config(
    page_title="LeadX Pro Scraper",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ LeadX Pro Email Scraper (Excel Style Output)")
st.write("Website → Email-1, Email-2, Email-3 ... format 🚀")

# ================= INPUT =================
urls_input = st.text_area("Enter Websites (one per line)")

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

COMMON_PATHS = [
    "/", "/contact", "/contact-us", "/about",
    "/support", "/faq", "/privacy", "/terms"
]

# ================= CLEAN EMAILS =================
def clean_emails(emails):
    clean = []
    for e in emails:
        if re.match(EMAIL_REGEX, e):
            if not any(x in e.lower() for x in ["png", "jpg", "webp", "gif"]):
                clean.append(e)

    # remove duplicates + max 5
    return list(dict.fromkeys(clean))[:5]

# ================= SCRAPER =================
def scrape_site(url):
    try:
        all_emails = set()

        for path in COMMON_PATHS:
            full_url = url.rstrip("/") + path

            r = requests.get(
                full_url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            emails = re.findall(EMAIL_REGEX, r.text)

            for e in clean_emails(emails):
                all_emails.add(e)

            if len(all_emails) >= 5:
                break

        emails_list = list(all_emails)[:5]

        return url, emails_list

    except:
        return url, []

# ================= RUN =================
if st.button("🚀 Start Scraping"):

    urls = list(set([u.strip() for u in urls_input.split("\n") if u.strip()]))

    results = []
    progress = st.progress(0)

    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(scrape_site, u if u.startswith("http") else "https://" + u)
                   for u in urls]

        for i, f in enumerate(futures):
            url, emails = f.result()

            # FIXED FORMAT (COLUMN STYLE)
            row = {
                "Website": url,
                "Email-1": emails[0] if len(emails) > 0 else "",
                "Email-2": emails[1] if len(emails) > 1 else "",
                "Email-3": emails[2] if len(emails) > 2 else "",
                "Email-4": emails[3] if len(emails) > 3 else "",
                "Email-5": emails[4] if len(emails) > 4 else "",
            }

            results.append(row)

            progress.progress((i + 1) / len(urls))

    df = pd.DataFrame(results)

    st.success("Scraping Completed ✅")

    # ================= TABLE =================
    st.dataframe(df, use_container_width=True)

    # ================= DOWNLOAD =================
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Excel CSV",
        csv,
        "leadx_pro.xlsx.csv",
        "text/csv"
    )
