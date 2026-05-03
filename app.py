import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= CONFIG =================
st.set_page_config(
    page_title="LeadX Pro",
    page_icon="⚡",
    layout="wide"
)

# ================= ADVANCED UI =================
st.markdown("""
<style>

/* ANIMATED GRADIENT BACKGROUND */
body {
    background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #4c1d95);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
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
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 15px;
    backdrop-filter: blur(12px);
    transition: 0.3s;
    text-align: center;
}

.card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 50px rgba(0,0,0,0.6);
}

/* BUTTON */
.stButton button {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    border-radius: 12px;
    padding: 12px 25px;
    font-weight: bold;
    border: none;
}

.stButton button:hover {
    transform: scale(1.05);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0f172a;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.image("https://i.imgur.com/8Km9tLL.png", width=150)

st.sidebar.markdown("""
### 🚀 LeadX Pro  
*"Build once. Scale forever."*

💡 *Turn websites into real business leads*
""")

menu = st.sidebar.selectbox(
    "📌 Navigation",
    ["🏠 Dashboard", "ℹ About", "📞 Contact", "📄 Terms", "🔐 Privacy", "❓ FAQ"]
)

# ================= STATIC PAGES =================
if menu == "ℹ About":
    st.title("About LeadX Pro")
    st.write("LeadX Pro is an advanced SaaS tool for extracting official business emails from websites.")

elif menu == "📞 Contact":
    st.title("Contact")
    st.write("support@leadxpro.com")

elif menu == "📄 Terms":
    st.title("Terms & Conditions")
    st.write("Use only for legal business purposes.")

elif menu == "🔐 Privacy":
    st.title("Privacy Policy")
    st.write("We do not store any user data.")

elif menu == "❓ FAQ":
    st.title("FAQ")
    st.markdown("""
- Max 5 emails per website  
- No duplicate websites  
- Works on public data only  
""")

# ================= MAIN DASHBOARD =================
else:

    # HERO
    st.markdown("""
    <div class="hero">
        <h1>⚡ LeadX Pro</h1>
        <h3>Extract High-Quality Business Emails in Seconds</h3>
        <p>Fast • Clean • Professional Lead Generation Tool</p>
    </div>
    """, unsafe_allow_html=True)

    # FEATURES
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
        <h3>⚡ Fast Engine</h3>
        <p>Multi-threaded scraping for lightning speed</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h3>🎯 Smart Emails</h3>
        <p>Extract only relevant business emails</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
        <h3>📊 Clean Output</h3>
        <p>CRM-ready structured data</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # INPUT
    urls_input = st.text_area("Enter Websites (one per line)")

    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

    COMMON_PATHS = [
        "/", "/contact", "/contact-us", "/about",
        "/support", "/faq", "/privacy", "/terms"
    ]

    def clean_emails(emails):
        clean = []
        for e in emails:
            if re.match(EMAIL_REGEX, e):
                if not any(x in e.lower() for x in ["png", "jpg", "webp", "gif"]):
                    clean.append(e)
        return list(dict.fromkeys(clean))[:5]

    def scrape_site(url):
        try:
            found = set()

            for path in COMMON_PATHS:
                full = url.rstrip("/") + path

                r = requests.get(full, timeout=8, headers={"User-Agent": "Mozilla/5.0"})

                emails = re.findall(EMAIL_REGEX, r.text)

                for e in clean_emails(emails):
                    found.add(e)

                if len(found) >= 5:
                    break

            return url, list(found)[:5]

        except:
            return url, []

    # RUN
    if st.button("🚀 Start Scraping"):

        urls = list(set([u.strip() for u in urls_input.split("\n") if u.strip()]))

        results = []
        progress = st.progress(0)

        with st.spinner("Scraping in progress... ⏳"):

            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(scrape_site, u if u.startswith("http") else "https://" + u)
                           for u in urls]

                for i, f in enumerate(futures):
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

                    progress.progress((i + 1) / len(urls))

        df = pd.DataFrame(results)

        st.success("✅ Scraping Completed Successfully!")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇ Download CSV",
            df.to_csv(index=False),
            "leadx_pro.csv",
            "text/csv"
        )
