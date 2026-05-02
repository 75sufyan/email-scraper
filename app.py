import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="LeadX Pro Scraper",
    page_icon="⚡",
    layout="wide"
)

# ================= CUSTOM STYLE (ECONIX STYLE) =================
st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    color: white;
}

h1, h2, h3 {
    color: #ffffff;
}

.sidebar .sidebar-content {
    background: #111827;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
    margin-bottom: 10px;
}

.stButton button {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR PROFILE =================
st.sidebar.image("https://kommodo.ai/i/jgrsiXtQ3CuYlMPJl2Gi", width=150)

st.sidebar.markdown("""
### 💡 LeadX Pro Tool  
*"Turn websites into real business leads"*
""")

menu = st.sidebar.selectbox(
    "📌 Navigation",
    ["🏠 Dashboard", "ℹ About", "📞 Contact", "📄 Terms", "🔐 Privacy", "❓ FAQ"]
)

# ================= STATIC PAGES =================
if menu == "ℹ About":
    st.title("ℹ About Tool")
    st.write("Advanced SaaS scraper for extracting official business emails.")

elif menu == "📞 Contact":
    st.title("📞 Contact")
    st.write("support@leadxpro.com")

elif menu == "📄 Terms":
    st.title("📄 Terms & Conditions")
    st.write("Use only for legal lead generation purposes.")

elif menu == "🔐 Privacy":
    st.title("🔐 Privacy Policy")
    st.write("We do not store or save any user data.")

elif menu == "❓ FAQ":
    st.title("❓ FAQ")
    st.write("Max 5 official emails per website. Duplicate domains removed.")

# ================= MAIN DASHBOARD =================
else:

    st.title("⚡ LeadX Pro Email Scraper")
    st.write("Scrape 1000+ websites with smart crawling 🚀")

    urls_input = st.text_area("Enter URLs (one per line)")

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

    # ================= RUN =================
    if st.button("🚀 Start Ultra Scraping"):

        urls = list(set([u.strip() for u in urls_input.split("\n") if u.strip()]))

        results = []
        progress = st.progress(0)

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(scrape_site, u if u.startswith("http") else "https://" + u)
                       for u in urls]

            for i, f in enumerate(futures):
                url, emails = f.result()

                if emails:
                    email_string = " | ".join([f"email {i+1}: {e}" for i, e in enumerate(emails)])
                    results.append([url, email_string])
                else:
                    results.append([url, "No Email Found"])

                progress.progress((i + 1) / len(urls))

        df = pd.DataFrame(results, columns=["Website", "Emails"])

        st.success("Scraping Completed 🚀")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇ Download CSV",
            df.to_csv(index=False),
            "leadx_pro.csv",
            "text/csv"
        )
