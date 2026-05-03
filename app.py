import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= CONFIG =================
st.set_page_config(page_title="LeadX Pro", page_icon="⚡", layout="wide")

# ================= ADVANCED UI =================
st.markdown("""
<style>

/* ANIMATED BACKGROUND */
body {
    background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #4c1d95);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
    color: white;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* HERO */
.hero {
    padding: 50px;
    border-radius: 20px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    text-align: center;
    color: white;
    margin-bottom: 20px;
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    text-align: center;
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-10px);
}

/* BUTTON */
.stButton button {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    border-radius: 12px;
    padding: 12px 25px;
    font-weight: bold;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0f172a;
}

/* PROFILE */
.profile-container {
    text-align: center;
    margin-top: 20px;
}

/* GLOW RING */
.profile-img {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    object-fit: cover;
    padding: 4px;
    background: linear-gradient(45deg, #6366f1, #a855f7, #22d3ee);
    animation: rotate 6s linear infinite;
}

@keyframes rotate {
    100% { transform: rotate(360deg); }
}

/* INNER IMAGE */
.profile-img img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
}

/* NAME */
.profile-name {
    font-size: 18px;
    font-weight: bold;
    margin-top: 10px;
}

/* ONLINE DOT */
.online-dot {
    width: 10px;
    height: 10px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
    margin-left: 5px;
}

/* SOCIAL ICONS */
.social a {
    margin: 0 8px;
    text-decoration: none;
    font-size: 18px;
    color: #cbd5f5;
}
.social a:hover {
    color: #ffffff;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.markdown("""
<div class="profile-container">

    <div class="profile-img">
        <img src="profile.jpg">
    </div>

    <div class="profile-name">
        Sufyan SA <span class="online-dot"></span>
    </div>

    <div style="font-size:12px; color:#aaa;">
        "Build tools. Build freedom."
    </div>

    <div class="social">
        <a href="https://linkedin.com" target="_blank">🔗</a>
        <a href="https://fiverr.com" target="_blank">💼</a>
        <a href="https://github.com" target="_blank">💻</a>
    </div>

</div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox(
    "📌 Navigation",
    ["🏠 Dashboard", "ℹ About", "📞 Contact", "📄 Terms", "🔐 Privacy", "❓ FAQ"]
)

# ================= STATIC PAGES =================
if menu == "ℹ About":
    st.title("About")
    st.write("Professional SaaS Email Scraper Tool")

elif menu == "📞 Contact":
    st.title("Contact")
    st.write("support@leadxpro.com")

elif menu == "📄 Terms":
    st.title("Terms")
    st.write("Use for legal purposes only")

elif menu == "🔐 Privacy":
    st.title("Privacy")
    st.write("No data stored")

elif menu == "❓ FAQ":
    st.title("FAQ")
    st.write("Max 5 emails per website")

# ================= MAIN =================
else:

    st.markdown("""
    <div class="hero">
        <h1>⚡ LeadX Pro</h1>
        <p>Extract High Quality Emails Instantly</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card">⚡ Fast Scraping</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">🎯 Smart Emails</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">📊 Clean Data</div>', unsafe_allow_html=True)

    urls_input = st.text_area("Enter Websites")

    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

    COMMON_PATHS = [
        "/", "/contact", "/contact-us", "/about",
        "/support", "/faq", "/privacy", "/terms"
    ]

    def scrape_site(url):
        try:
            found = set()
            for path in COMMON_PATHS:
                full = url.rstrip("/") + path
                r = requests.get(full, timeout=8)
                emails = re.findall(EMAIL_REGEX, r.text)
                for e in emails:
                    found.add(e)
                if len(found) >= 5:
                    break
            return url, list(found)[:5]
        except:
            return url, []

    if st.button("🚀 Start Scraping"):

        urls = list(set(urls_input.split("\n")))

        results = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(scrape_site, u if u.startswith("http") else "https://" + u)
                       for u in urls]

            for f in futures:
                url, emails = f.result()

                row = {
                    "Website": url,
                    "Email-1": emails[0] if len(emails) > 0 else "",
                    "Email-2": emails[1] if len(emails) > 1 else "",
                    "Email-3": emails[2] if len(emails) > 2 else "",
                    "Email-4": emails[3] if len(emails) > 3 else "",
                    "Email-5": emails[4] if len(emails) > 4 else "",
                }

                results.append(row)

        df = pd.DataFrame(results)

        st.dataframe(df)

        st.download_button("Download CSV", df.to_csv(index=False), "emails.csv")
