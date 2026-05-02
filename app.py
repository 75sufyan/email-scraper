import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ================= CONFIG =================
st.set_page_config(
    page_title="SaaS Email Scraper Pro",
    page_icon="⚡",
    layout="wide"
)

# ================= NAVIGATION =================
menu = st.sidebar.selectbox(
    "📌 Menu",
    ["🏠 Home", "📄 Terms", "🔐 Privacy", "📞 Contact", "ℹ About", "❓ FAQ"]
)

# ================= STATIC PAGES =================
if menu == "📄 Terms":
    st.title("📄 Terms & Conditions")
    st.write("Tool educational & lead generation purpose ke liye hai. Spam strictly forbidden.")

elif menu == "🔐 Privacy":
    st.title("🔐 Privacy Policy")
    st.write("We do not store user data. All scraping is real-time and temporary.")

elif menu == "📞 Contact":
    st.title("📞 Contact Page")
    st.write("For support: support@example.com")

elif menu == "ℹ About":
    st.title("ℹ About")
    st.write("This tool extracts official business emails from public websites.")

elif menu == "❓ FAQ":
    st.title("❓ FAQ")

    st.markdown("""
    **Q: Kitne emails milte hain?**  
    A: Max 5 official emails per website

    **Q: Spam emails milte hain?**  
    A: Nahi, sirf official emails

    **Q: Free hai?**  
    A: Haan, currently free version
    """)

# ================= MAIN APP =================
else:

    st.title("⚡ SaaS Email Scraper Pro")
    st.write("Extract official business emails (max 5 per website) 🚀")

    domains = st.text_area("Enter websites (one per line)")

    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"

    COMMON_PATHS = [
        "/", "/contact", "/contact-us", "/about",
        "/support", "/faq", "/privacy", "/terms"
    ]

    def extract_official_emails(text):
        emails = re.findall(EMAIL_REGEX, text)

        clean = []
        for e in emails:
            if not any(x in e.lower() for x in ["png", "jpg", "webp", "gif"]):
                clean.append(e)

        # remove duplicates + limit 5
        return list(dict.fromkeys(clean))[:5]

    def scrape_site(url):
        try:
            found = set()

            for path in COMMON_PATHS:
                full_url = url.rstrip("/") + path

                r = requests.get(
                    full_url,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                emails = extract_official_emails(r.text)

                for e in emails:
                    found.add(e)

                # stop early if already 5 emails
                if len(found) >= 5:
                    break

            return url, list(found)[:5]

        except:
            return url, []

    # ================= RUN =================
    if st.button("🚀 Start Smart Scraping"):

        domain_list = [d.strip() for d in domains.split("\n") if d.strip()]

        results = []
        progress = st.progress(0)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(scrape_site, d if d.startswith("http") else "https://" + d)
                       for d in domain_list]

            for i, f in enumerate(futures):
                url, emails = f.result()

                if emails:
                    for e in emails:
                        results.append([url, e])
                else:
                    results.append([url, "Not Found"])

                progress.progress((i + 1) / len(domain_list))

        df = pd.DataFrame(results, columns=["Website", "Official Email"])

        st.success("Scraping Completed ✅")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇ Download CSV",
            df.to_csv(index=False),
            "official_emails.csv",
            "text/csv"
        )
