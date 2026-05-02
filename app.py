import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Email Scraper Pro 10X",
    page_icon="⚡",
    layout="wide"
)

# ================= UI =================
st.title("⚡ Email Scraper Pro 10X")
st.write("Fast + Clean + Business Email Extractor 🚀")

# ================= INPUT =================
domains = st.text_area("Enter websites (one per line)")

# ================= EMAIL PATTERN =================
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

# ================= FILTERS =================
BUSINESS_PREFIX = ["info", "contact", "support", "sales", "hello"]

def is_valid_email(email):
    if not re.match(EMAIL_REGEX, email):
        return False
    if any(x in email.lower() for x in ["png", "jpg", "webp", "svg", "gif"]):
        return False
    return True

def is_business(email):
    return any(email.lower().startswith(p) for p in BUSINESS_PREFIX)

# ================= SCRAPER =================
def scrape_site(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        emails = re.findall(EMAIL_REGEX, r.text)

        clean = set()

        for e in emails:
            if is_valid_email(e):
                clean.add(e)

        return url, list(clean)

    except:
        return url, []

# ================= RUN =================
if st.button("🚀 Start 10X Scraping"):

    domain_list = [d.strip() for d in domains.split("\n") if d.strip()]

    if not domain_list:
        st.warning("Please enter websites")
    else:

        results = []
        progress = st.progress(0)

        # FAST PARALLEL SCRAPING
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(scrape_site, d if d.startswith("http") else "https://" + d)
                       for d in domain_list]

            for i, f in enumerate(futures):
                url, emails = f.result()

                if emails:
                    for e in emails:
                        if is_business(e):
                            results.append([url, e, "Business"])
                        else:
                            results.append([url, e, "General"])
                else:
                    results.append([url, "Not Found", "N/A"])

                progress.progress((i + 1) / len(domain_list))

        # ================= DATAFRAME =================
        df = pd.DataFrame(results, columns=["Website", "Email", "Type"])

        st.success("Scraping Completed ✅")

        st.dataframe(df, use_container_width=True)

        # ================= DOWNLOAD =================
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            csv,
            "emails_10x.csv",
            "text/csv"
        )
