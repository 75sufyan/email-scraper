import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= CONFIG =================
st.set_page_config(page_title="Econix Lead Engine", page_icon="⚡", layout="wide")

# ================= CSS FIXED =================
st.markdown("""
<style>

/* BACKGROUND */
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
    padding: 40px;
    border-radius: 20px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    text-align: center;
    color: white;
    margin-bottom: 25px;
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
    transform: translateY(-6px);
}

/* BUTTON */
.stButton button {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0f172a;
}

/* PROFILE */
.profile-box {
    text-align: center;
    margin-top: 10px;
}

/* GLOW RING */
.profile-img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    padding: 3px;
    background: linear-gradient(45deg, #6366f1, #a855f7, #22d3ee);
    margin: auto;
}
.profile-img img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}

/* NAME */
.profile-name {
    margin-top: 10px;
    font-size: 16px;
    font-weight: bold;
}

/* ONLINE DOT */
.online {
    height: 8px;
    width: 8px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
}

/* SOCIAL */
.social a {
    margin: 0 6px;
    text-decoration: none;
    font-size: 16px;
    color: #aaa;
}
.social a:hover {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR CLEAN =================
st.sidebar.markdown("""
<div class="profile-box">

    <div class="profile-img">
        <img src="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/profile.jpg">
    </div>

    <div class="profile-name">
        Sufyan SA <span class="online"></span>
    </div>

    <div style="font-size:12px; color:#aaa;">
        Build tools. Build freedom.
    </div>

    <div class="social">
        <a href="https://linkedin.com" target="_blank">🔗</a>
        <a href="https://fiverr.com" target="_blank">💼</a>
        <a href="https://github.com" target="_blank">💻</a>
    </div>

</div>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "About", "Contact", "Terms", "Privacy", "FAQ"]
)

# ================= STATIC PAGES =================
if menu == "About":
    st.title("About")
    st.write("Econix Lead Engine extracts official emails from websites.")

elif menu == "Contact":
    st.title("Contact")
    st.write("support@econixdigital.com")

elif menu == "Terms":
    st.title("Terms")
    st.write("Use only for legal purposes.")

elif menu == "Privacy":
    st.title("Privacy")
    st.write("No data stored.")

elif menu == "FAQ":
    st.title("FAQ")
    st.write("Max 5 emails per website.")

# ================= MAIN =================
else:

    st.markdown("""
    <div class="hero">
        <h1>⚡ Econix Lead Engine</h1>
        <p>Extract High Quality Business Emails Instantly</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card">⚡ Fast Scraping</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">🎯 Smart Emails</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">📊 Clean Output</div>', unsafe_allow_html=True)

    urls_input = st.text_area("Enter Websites (one per line)")

    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

    PATHS = ["/", "/contact", "/about", "/faq", "/support", "/privacy", "/terms"]

    def scrape(url):
        try:
            found = set()
            for p in PATHS:
                r = requests.get(url.rstrip("/") + p, timeout=8)
                emails = re.findall(EMAIL_REGEX, r.text)
                for e in emails:
                    if "png" not in e:
                        found.add(e)
                if len(found) >= 5:
                    break
            return url, list(found)[:5]
        except:
            return url, []

    if st.button("🚀 Start Scraping"):

        urls = list(set([u.strip() for u in urls_input.split("\n") if u.strip()]))

        results = []

        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(scrape, u if u.startswith("http") else "https://" + u) for u in urls]

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

        st.success("Done ✅")

        st.dataframe(df, use_container_width=True)

        st.download_button("Download CSV", df.to_csv(index=False), "emails.csv")
