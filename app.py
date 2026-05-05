import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Econix Email Finder", page_icon="⚡", layout="wide")

# ================= SESSION =================
if "df" not in st.session_state:
    st.session_state.df = None

# ================= CSS (UNCHANGED) =================
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
<p>Smart scraping • No garbage • Max 5 clean emails per site</p>
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

def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")

# 🔥 ADVANCED FILTER
def is_valid(email, domain):
    email = email.lower().strip()

    if domain not in email:
        return False

    bad_words = ["example","test","sample","your","name@","email@","company","domain"]
    if any(b in email for b in bad_words):
        return False

    public = ["gmail.com","yahoo.com","hotmail.com","outlook.com"]
    if any(p in email for p in public):
        return False

    return True

PATHS = ["/","/contact"]

def fetch(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=6).text
    except:
        return ""

def scrape(url):
    domain = get_domain(url)
    found = set()

    for path in PATHS:
        html = fetch(urljoin(url, path))
        emails = re.findall(EMAIL_REGEX, html)

        for e in emails:
            if is_valid(e, domain):
                found.add(e)

        if len(found) >= 5:
            break

    return url, list(found)[:5]

# ================= SCRAPE =================
if st.button("🚀 Start Scraping"):

    urls = list(set([u.strip() for u in urls_input.split("\n") if u.strip()]))

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

# ================= RESULT =================
if st.session_state.df is not None:

    st.success(f"✅ {len(st.session_state.df)} Websites Processed")
    st.dataframe(st.session_state.df, use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        st.session_state.df.to_csv(index=False),
        "emails.csv"
    )
