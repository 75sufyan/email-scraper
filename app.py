import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Econix Email Finder", page_icon="⚡", layout="wide")

# ================= SESSION =================
if "df" not in st.session_state:
    st.session_state.df = None

# ================= UI (UNCHANGED) =================
st.markdown("""<style>
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
.navbar {display:flex;justify-content:space-between;padding:15px 25px;background: rgba(255,255,255,0.05);border-radius:14px;margin-bottom:20px;}
.logo { font-size:22px; font-weight:bold; }
.menu span { margin-left:20px; cursor:pointer; color:#ddd; }
.menu span:hover { color:white; }
.hero {padding:50px;border-radius:20px;background: linear-gradient(135deg,#4709e5,#9333ea);text-align:center;margin-bottom:25px;box-shadow:0 10px 30px rgba(0,0,0,0.4);}
.card {background: rgba(255,255,255,0.07);padding:25px;border-radius:16px;text-align:center;transition:0.3s;}
.card:hover {transform:translateY(-10px) scale(1.02);background: rgba(255,255,255,0.12);}
.stButton button {background: linear-gradient(90deg,#9333ea,#c084fc);border:none;color:white;border-radius:12px;font-weight:bold;padding:10px 20px;font-size:16px;}
section[data-testid="stSidebar"] { background:#0f172a; }
</style>""", unsafe_allow_html=True)

# ================= INPUT =================
urls_input = st.text_area("Enter Websites (one per line)")

EMAIL_REGEX = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}\b"

# 🔥 FILTERS
BAD_KEYWORDS = [
    "example","test","sample","domain","your","you",
    "png","jpg","jpeg","svg","webp","css","js",
    "wixpress","sentry","placeholder","email.com","company.com"
]

def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")

def is_valid(email, domain):
    email = email.lower().strip()

    if any(b in email for b in BAD_KEYWORDS):
        return False

    # domain match (VERY IMPORTANT FIX)
    if domain not in email:
        return False

    return True

def clean_email(e):
    return e.replace("u003e","").replace("%20","").strip().lower()

PATHS = ["/","/contact","/about","/support","/privacy","/terms"]

def scrape(url):
    domain = get_domain(url)
    found = set()

    for p in PATHS:
        try:
            r = requests.get(url.rstrip("/") + p, timeout=8, headers={"User-Agent":"Mozilla/5.0"})
            emails = re.findall(EMAIL_REGEX, r.text)

            for e in emails:
                e = clean_email(e)

                if is_valid(e, domain):
                    found.add(e)

            if len(found) >= 5:
                break

        except:
            continue

    return list(found)[:5]

# ================= SCRAPE =================
if st.button("🚀 Start Scraping"):

    # ⚠️ ORDER FIX (IMPORTANT)
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    formatted_urls = [
        u if u.startswith("http") else "https://" + u
        for u in urls
    ]

    results_dict = {}

    with st.spinner("Scraping like a PRO..."):
        with ThreadPoolExecutor(max_workers=10) as executor:

            future_to_url = {
                executor.submit(scrape, url): url
                for url in formatted_urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    emails = future.result()
                except:
                    emails = []

                results_dict[url] = emails

    # ✅ ORDER PRESERVED OUTPUT
    final_rows = []
    for url in formatted_urls:
        emails = results_dict.get(url, [])

        row = {
            "Website": url,
            "Email-1": emails[0] if len(emails)>0 else "",
            "Email-2": emails[1] if len(emails)>1 else "",
            "Email-3": emails[2] if len(emails)>2 else "",
            "Email-4": emails[3] if len(emails)>3 else "",
            "Email-5": emails[4] if len(emails)>4 else "",
        }

        final_rows.append(row)

    df = pd.DataFrame(final_rows)

    st.session_state.df = df

# ================= OUTPUT =================
if st.session_state.df is not None:

    st.success(f"✅ {len(st.session_state.df)} Websites Processed")
    st.dataframe(st.session_state.df, use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        st.session_state.df.to_csv(index=False),
        "emails_clean.csv"
    )
