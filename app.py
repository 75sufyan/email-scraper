import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from langdetect import detect
from deep_translator import GoogleTranslator

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Econix Email Finder", page_icon="⚡", layout="wide")

if "df" not in st.session_state:
    st.session_state.df = None

# ================= CSS (UNCHANGED UI) =================
st.markdown("""
<style>
html, body {
    background: linear-gradient(-45deg,#4709e5,#6d28d9,#9333ea,#c084fc);
    background-size: 400% 400%;
    animation: bg 12s ease infinite;
    color: white;
}
@keyframes bg {
    0%{background-position:0%}
    50%{background-position:100%}
    100%{background-position:0%}
}

.navbar {
    display:flex;
    justify-content:space-between;
    padding:15px 25px;
    background: rgba(255,255,255,0.05);
    border-radius:14px;
    margin-bottom:20px;
}
.logo { font-size:22px; font-weight:bold; }
.menu span { margin-left:20px; cursor:pointer; color:#ddd; }

.hero {
    padding:50px;
    border-radius:20px;
    background: linear-gradient(135deg,#4709e5,#9333ea);
    text-align:center;
    margin-bottom:25px;
}

.card {
    background: rgba(255,255,255,0.07);
    padding:25px;
    border-radius:16px;
}
.stButton button {
    background: linear-gradient(90deg,#9333ea,#c084fc);
    border:none;
    color:white;
    border-radius:12px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.markdown("""
<div class="navbar">
<div class="logo">⚡ Econix Email Finder</div>
<div class="menu">
<span>Dashboard</span>
<span>Docs</span>
<span>Support</span>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>Find Real Business Emails Instantly</h1>
<p>Smart scraping • JS-safe mode • Max 5 clean emails per site</p>
</div>
""", unsafe_allow_html=True)

urls_input = st.text_area("Enter Websites (one per line)")

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

PATHS = ["/","/contact","/contact-us","/about","/support","/team"]

# ================= HELPERS =================
def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")

def clean_email(e):
    return e.lower().replace("[at]","@").replace("[dot]",".")

def is_valid(email):
    bad = ["png","jpg","css","js","example","test"]
    return not any(b in email for b in bad)

# ================= TRANSLATION =================
def smart_translate(text):
    try:
        if len(text) < 50:
            return text
        lang = detect(text)
        if lang == "en":
            return text
        return GoogleTranslator(source=lang, target='en').translate(text[:3000])
    except:
        return text

# ================= SAFE FETCH (NO PLAYWRIGHT CRASH) =================
def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.text
    except:
        return ""

# ================= CATEGORY =================
def detect_category(text):
    t = text.lower()
    if "casino" in t or "bet" in t:
        return "Casino / Betting"
    if "food" in t or "restaurant" in t:
        return "Restaurant"
    if "shop" in t:
        return "Ecommerce"
    if "blog" in t:
        return "Blog"
    if "agency" in t:
        return "Business"
    return "Unknown / Misc"

# ================= SCRAPER =================
def scrape(url):
    found = set()
    all_text = ""

    for path in PATHS:
        try:
            full = urljoin(url, path)
            html = fetch_html(full)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")

            # emails
            emails = re.findall(EMAIL_REGEX, html)

            for a in soup.find_all("a", href=True):
                if "mailto:" in a['href']:
                    emails.append(a['href'].replace("mailto:",""))

            for e in emails:
                e = clean_email(e)
                if is_valid(e):
                    found.add(e)

            text = soup.get_text(" ", strip=True)
            all_text += text

            translated = smart_translate(text)
            emails2 = re.findall(EMAIL_REGEX, translated)

            for e in emails2:
                e = clean_email(e)
                if is_valid(e):
                    found.add(e)

            if len(found) >= 5:
                break

        except:
            continue

    if not found:
        cat = detect_category(all_text)
        return url, [f"No Email | Category: {cat}"]

    return url, list(found)[:5]

# ================= RUN =================
if st.button("🚀 Start Scraping"):

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    results = []

    with st.spinner("Scraping like a PRO..."):

        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = [
                ex.submit(scrape, u if u.startswith("http") else "https://" + u)
                for u in urls
            ]

            for f in futures:
                url, emails = f.result()

                results.append({
                    "Website": url,
                    "Email-1": emails[0] if len(emails)>0 else "",
                    "Email-2": emails[1] if len(emails)>1 else "",
                    "Email-3": emails[2] if len(emails)>2 else "",
                    "Email-4": emails[3] if len(emails)>3 else "",
                    "Email-5": emails[4] if len(emails)>4 else "",
                })

    df = pd.DataFrame(results)
    st.session_state.df = df

# ================= OUTPUT =================
if st.session_state.df is not None:
    st.success(f"✅ {len(st.session_state.df)} Websites Processed")
    st.dataframe(st.session_state.df, use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        st.session_state.df.to_csv(index=False),
        "emails.csv"
    )
