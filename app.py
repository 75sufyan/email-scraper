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
}
.card {
    background: rgba(255,255,255,0.07);
    padding:25px;
    border-radius:16px;
    text-align:center;
}
.stButton button {
    background: linear-gradient(90deg,#9333ea,#c084fc);
    border:none;
    color:white;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.markdown('<div class="navbar"><div class="logo">⚡ Econix Email Finder</div></div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>Find Real Business Emails Instantly</h1></div>', unsafe_allow_html=True)

urls_input = st.text_area("Enter Websites (one per line)")

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ================= HELPERS =================
def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")

def is_valid(email, domain):
    email = email.lower()

    if domain not in email:
        return False

    bad = ["example","test","sample","your","png","jpg","css","js"]
    if any(b in email for b in bad):
        return False

    return True

PATHS = ["/","/contact","/about","/support","/privacy"]

def scrape(url):
    domain = get_domain(url)
    found = set()

    for path in PATHS:
        try:
            r = requests.get(urljoin(url, path), headers=HEADERS, timeout=6)

            emails = re.findall(EMAIL_REGEX, r.text)

            for e in emails:
                if is_valid(e, domain):
                    found.add(e)

            if len(found) >= 5:
                break

        except:
            continue

    return url, list(found)[:5]

# ================= BATCH SYSTEM =================
BATCH_SIZE = 50   # 🔥 main fix

def process_batches(urls):
    results = []

    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i:i+BATCH_SIZE]

        with ThreadPoolExecutor(max_workers=5) as ex:  # 🔥 reduced threads

            futures = [
                ex.submit(scrape, u if u.startswith("http") else "https://" + u)
                for u in batch
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

    return results

# ================= SCRAPE =================
if st.button("🚀 Start Scraping"):

    urls = list(set([u.strip() for u in urls_input.split("\n") if u.strip()]))

    with st.spinner("Scraping like a PRO..."):

        results = process_batches(urls)

    df = pd.DataFrame(results)

    st.session_state.df = df

# ================= RESULT =================
if st.session_state.df is not None:

    st.success(f"✅ {len(st.session_state.df)} Websites Processed")

    # 🔥 memory safe display
    st.dataframe(st.session_state.df.head(300), use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        st.session_state.df.to_csv(index=False),
        "emails.csv"
    )
