import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Econix Email Finder", page_icon="⚡", layout="wide")

# ================= CSS =================
st.markdown("""
<style>

/* ===== BACKGROUND ===== */
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

/* ===== NAVBAR ===== */
.navbar {
    display:flex;
    justify-content:space-between;
    padding:15px 25px;
    background: rgba(255,255,255,0.05);
    border-radius:14px;
    margin-bottom:20px;
}
.logo {
    font-size:22px;
    font-weight:bold;
}
.menu span {
    margin-left:20px;
    cursor:pointer;
    color:#ddd;
}
.menu span:hover {
    color:white;
}

/* ===== HERO ===== */
.hero {
    padding:50px;
    border-radius:20px;
    background: linear-gradient(135deg,#4709e5,#9333ea);
    text-align:center;
    margin-bottom:25px;
    box-shadow:0 10px 30px rgba(0,0,0,0.4);
}

/* ===== CARDS ===== */
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

/* ===== BUTTON ===== */
.stButton button {
    background: linear-gradient(90deg,#9333ea,#c084fc);
    border:none;
    color:white;
    border-radius:12px;
    font-weight:bold;
    padding:10px 20px;
    font-size:16px;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background:#0f172a;
}

/* ===== PROFILE ===== */
.profile-box {
    text-align:center;
}

/* GLOW RING */
.profile-img {
    width:110px;
    height:110px;
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
    width:100%;
    height:100%;
    border-radius:50%;
    object-fit:cover;
}

/* NAME */
.profile-name {
    margin-top:10px;
    font-weight:bold;
}

/* ONLINE DOT */
.online {
    height:8px;
    width:8px;
    background:#22c55e;
    border-radius:50%;
    display:inline-block;
}

/* SOCIAL */
.social a {
    margin:0 6px;
    color:#aaa;
    text-decoration:none;
    font-size:18px;
}
.social a:hover {
    color:white;
}

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
<a href="https://linkedin.com" target="_blank">🔗</a>
<a href="https://fiverr.com" target="_blank">💼</a>
<a href="https://github.com" target="_blank">💻</a>
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
PATHS = ["/","/contact","/about","/faq","/support","/privacy","/terms"]

# ❌ junk filter
def is_valid(email):
    bad = ["png","jpg","jpeg","webp","svg","css","js","example","domain"]
    return not any(b in email.lower() for b in bad)

def scrape(url):
    try:
        found=set()

        for p in PATHS:
            try:
                r=requests.get(url.rstrip("/")+p,timeout=8)
                emails=re.findall(EMAIL_REGEX,r.text)

                for e in emails:
                    if is_valid(e):
                        found.add(e)

                if len(found)>=5:
                    break
            except:
                continue

        return url,list(found)[:5]

    except:
        return url,[]

# ================= SCRAPE =================
if st.button("🚀 Start Scraping"):

    urls=list(set([u.strip() for u in urls_input.split("\n") if u.strip()]))

    results=[]

    with st.spinner("Scraping like a PRO..."):
        with ThreadPoolExecutor(max_workers=15) as ex:

            futures=[
                ex.submit(scrape, u if u.startswith("http") else "https://"+u)
                for u in urls
            ]

            for f in futures:
                url,emails=f.result()

                row={
                    "Website":url,
                    "Email-1":emails[0] if len(emails)>0 else "",
                    "Email-2":emails[1] if len(emails)>1 else "",
                    "Email-3":emails[2] if len(emails)>2 else "",
                    "Email-4":emails[3] if len(emails)>3 else "",
                    "Email-5":emails[4] if len(emails)>4 else "",
                }
                results.append(row)

    df=pd.DataFrame(results)

    st.success(f"✅ {len(df)} Websites Processed")
    st.dataframe(df,use_container_width=True)

    st.download_button("📥 Download CSV",df.to_csv(index=False),"emails.csv")
