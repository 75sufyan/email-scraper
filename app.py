import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# 🌍 NEW IMPORTS (JS + Translation)
from langdetect import detect
from deep_translator import GoogleTranslator
from playwright.sync_api import sync_playwright

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Econix Email Finder", page_icon="⚡", layout="wide")

# ================= SESSION =================
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
.menu span:hover { color:white; }

.hero {
    padding:50px;
    border-radius:20px;
    background: linear-gradient(135deg,#4709e5,#9333ea);
    text-align:center;
    margin-bottom:25px;
    box-shadow:0 10px 30px rgba(0,0,0,0.4);
}

.card {
    background: rgba(255,255,255,0.07);
    padding:25px;
    border-radius:16px;
    text-align:center;
    transition:0.3s;
}
.card:hover {
    transform:translateY(-10px) scale(1.02);
    background: rgba(255,255,255,0.12);
}

.stButton button {
    background: linear-gradient(90deg,#9333ea,#c084fc);
    border:none;
    color:white;
    border-radius:12px;
    font-weight:bold;
    padding:10px 20px;
    font-size:16px;
}

section[data-testid="stSidebar"] { background:#0f172a; }

.profile-box { text-align:center; }

.profile-img {
    width:110px; height:110px;
    border-radius:50%;
    padding:3px;
    background: linear-gradient(45deg,#9333ea,#c084fc,#22d3ee);
    animation: glow 3s infinite linear;
    margin:auto;
}
@keyframes glow {
    0%{filter:brightness(1)}
    50%{filter:brightness(1.5)}
    100%{filter:brightness(1)}
}
.profile-img img {
    width:100%; height:100%;
    border-radius:50%;
    object-fit:cover;
}
.profile-name { margin-top:10px; font-weight:bold; }

.online {
    height:8px; width:8px;
    background:#22c55e;
    border-radius:50%;
    display:inline-block;
}

.social a {
    margin:0 6px;
    color:#aaa;
    text-decoration:none;
    font-size:18px;
}
.social a:hover { color:white; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.markdown("""
<div class="profile-box">
<div class="profile-img">
<img src="https://raw.githubusercontent.com/75sufyan/email-scraper/main/profile.jpg">
</div>
<div class="profile-name">
Sufyan SA <span class="online"></span>
</div>
<div style="font-size:12px;color:#aaa;">
Build tools. Build freedom.
</div>
<div class="social">
<a href="#">🔗</a>
<a href="#">💼</a>
<a href="#">💻</a>
</div>
</div>
""", unsafe_allow_html=True)

# ================= NAVBAR =================
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

# ================= HERO =================
st.markdown("""
<div class="hero">
<h1>Find Real Business Emails Instantly</h1>
<p>Smart scraping • JS websites supported • Max 5 clean emails per site</p>
</div>
""", unsafe_allow_html=True)

# ================= CARDS =================
c1,c2,c3 = st.columns(3)
with c1:
    st.markdown('<div class="card">⚡ Fast Scraping</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="card">🎯 Smart Filter</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="card">📊 Clean CSV Output</div>', unsafe_allow_html=True)

# ================= INPUT =================
urls_input = st.text_area("Enter Websites (one per line)")

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

HEADERS = {"User-Agent": "Mozilla/5.0"}

PATHS = ["/","/contact","/about","/support","/privacy"]

# ================= DOMAIN =================
def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")

# ================= VALID EMAIL =================
def is_valid(email, domain):
    email = email.lower()

    if domain not in email:
        return False

    bad = ["example","test","sample","your","png","jpg","css","js"]
    if any(b in email for b in bad):
        return False

    return True

# ================= TRANSLATOR =================
def translate_to_english(text):
    try:
        if len(text) < 20:
            return text

        lang = detect(text)
        if lang == "en":
            return text

        return GoogleTranslator(source=lang, target='en').translate(text)

    except:
        return text

# ================= JS RENDER (PLAYWRIGHT) =================
def fetch_rendered_html(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()
            return html
    except:
        return None

# ================= SCRAPER =================
def scrape(url):
    domain = get_domain(url)
    found = set()

    for path in PATHS:
        try:
            full = urljoin(url, path)

            # 🔥 JS render first
            html = fetch_rendered_html(full)

            # fallback
            if not html:
                r = requests.get(full, headers=HEADERS, timeout=10)
                html = r.text

            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ", strip=True)

            # 🌍 translate
            text = translate_to_english(text)

            emails = re.findall(EMAIL_REGEX, text)

            for e in emails:
                if is_valid(e, domain):
                    found.add(e)

            if len(found) >= 5:
                break

        except:
            continue

    return url, list(found)[:5]

# ================= RUN =================
if st.button("🚀 Start Scraping"):

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    results = []

    with st.spinner("Scraping like a PRO..."):

        with ThreadPoolExecutor(max_workers=10) as ex:
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
