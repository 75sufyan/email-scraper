import streamlit as st
import requests
import re
import pandas as pd

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Email Scraper Pro",
    page_icon="⚡",
    layout="wide"
)

# ================= CUSTOM CSS (PRERENO STYLE) =================
st.markdown("""
<style>

body {
    background-color: #0f172a;
}

.main {
    background-color: #0f172a;
}

h1, h2, h3 {
    color: #ffffff;
}

.stTextArea textarea {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
}

.stButton button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
    border: none;
}

.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
    margin-top: 10px;
    color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.title("⚡ Email Scraper Pro Dashboard")
st.write("Extract business emails from websites in seconds 🚀")

# ================= INPUT SECTION =================
col1, col2 = st.columns([2,1])

with col1:
    domains = st.text_area("Enter Websites (one per line)")

with col2:
    st.markdown("""
    <div class="card">
        <h3>💡 How it works</h3>
        <p>1. Enter domains<br>
        2. Click scrape<br>
        3. Get emails instantly</p>
    </div>
    """, unsafe_allow_html=True)

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

def get_emails(url):
    try:
        r = requests.get(url, timeout=10)
        return list(set(re.findall(EMAIL_REGEX, r.text)))
    except:
        return []

# ================= SCRAPE BUTTON =================
if st.button("🚀 Start Scraping"):

    results = []
    progress = st.progress(0)

    domain_list = domains.split("\n")

    for i, d in enumerate(domain_list):
        d = d.strip()
        if not d:
            continue

        if not d.startswith("http"):
            d = "https://" + d

        emails = get_emails(d)

        if emails:
            for e in emails:
                results.append([d, e])
        else:
            results.append([d, "Not Found"])

        progress.progress((i+1)/len(domain_list))

    df = pd.DataFrame(results, columns=["Website", "Email"])

    st.success("Scraping Completed ✅")

    # ================= RESULT TABLE =================
    st.dataframe(df, use_container_width=True)

    # ================= DOWNLOAD =================
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇ Download CSV Report",
        csv,
        "emails.csv",
        "text/csv"
    )
