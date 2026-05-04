import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Econix Email Finder", page_icon="⚡", layout="wide")

# ================= SESSION STATE =================
if "data" not in st.session_state:
    st.session_state.data = None

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

/* NAVBAR */
.navbar {
    display:flex;
    justify-content:space-between;
    padding:15px 25px;
    background: rgba(255,255,255,0.05);
    border-radius:14px;
    margin-bottom:20px;
}
.logo { font-size:22px; font-weight:bold; }

/* HERO */
.hero {
    padding:50px;
    border-radius:20px;
    background: linear-gradient(135deg,#4709e5,#9333ea);
    text-align:center;
    margin-bottom:25px;
    box-shadow:0 10px 30px rgba(0,0,0,0.4);
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.07);
    padding:25px;
    border-radius:16px;
    text-align:center;
    transition:0.3s;
}
.card:hover {
    transform:translateY(-10px);
}

/* BUTTON */
.stButton button {
    background: linear-gradient(90deg,#9333ea,#c084fc);
    border:none;
    color:white;
    border-radius:12px;
    font-weight:bold;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background:#0f172a;
}

</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.markdown("""
<div class="navbar">
<div class="logo">⚡ Econix Email Finder</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>Find Real Business Emails Instantly</h1>
<p>Clean • Fast • Smart Extraction</p>
</div>
""", unsafe_allow_html=True)

# ================= INPUT =================
urls_input = st.text_area("Enter Websites (one per line)")

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"
PATHS = ["/","/contact","/about","/support","/privacy","/terms"]

# ================= FILTER =================
def is_valid(email):
    email = email.lower().strip()

    bad_keywords = [
        "png","jpg","jpeg","webp","svg","css","js",
        "example","domain","your","name","test",
        "company","email.com","wixpress","sentry",
        "cloudflare","firebase","amazonaws"
    ]

    if any(b in email for b in bad_keywords):
        return False

    if not re.match(EMAIL_REGEX, email):
        return False

    return True

# ================= SCRAPER =================
def scrape(url):
    try:
        found=set()

        for p in PATHS:
            try:
                r=requests.get(url.rstrip("/")+p,timeout=8)

                emails=re.findall(EMAIL_REGEX,r.text)

                for e in emails:
                    if is_valid(e):
                        found.add(e.lower())

                if len(found)>=5:
                    break

            except:
                continue

        # PRIORITY SORT
        priority = ["info","contact","hello","support","sales"]
        found = list(found)
        found = sorted(found, key=lambda x: 0 if any(p in x for p in priority) else 1)

        return url,found[:5]

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

    st.session_state.data = pd.DataFrame(results)

# ================= OUTPUT =================
if st.session_state.data is not None:

    st.success(f"✅ {len(st.session_state.data)} Websites Processed")

    st.dataframe(st.session_state.data, use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        st.session_state.data.to_csv(index=False),
        "emails.csv"
    )
