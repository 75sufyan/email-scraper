import streamlit as st
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# 🌍 Translation
from langdetect import detect
from deep_translator import GoogleTranslator

# 🔥 JS Render
from playwright.sync_api import sync_playwright

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Econix Email Finder", page_icon="⚡", layout="wide")

# ================= SESSION =================
if "df" not in st.session_state:
    st.session_state.df = None

# ================= UI (UNCHANGED) =================
st.markdown("<h1 style='text-align:center;'>⚡ Econix Email Finder</h1>", unsafe_allow_html=True)

urls_input = st.text_area("Enter Websites (one per line)")

# ================= CONFIG =================
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

PATHS = [
    "/", "/contact", "/contact-us", "/about",
    "/support", "/team", "/privacy", "/terms"
]

# ================= UTIL =================
def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")

def clean_email(e):
    e = e.lower()
    e = e.replace("[at]", "@").replace("(at)", "@")
    e = e.replace("[dot]", ".").replace("(dot)", ".")
    return e

def is_valid(email):
    bad = ["png","jpg","css","js","example","test"]
    return not any(b in email for b in bad)

# ================= SMART TRANSLATION =================
def smart_translate(text):
    try:
        if len(text) < 50:
            return text
        
        lang = detect(text)
        
        if lang == "en":
            return text
        
        return GoogleTranslator(source=lang, target='en').translate(text[:3000])
    
    except:
        return text

# ================= IMPORTANT TEXT =================
def extract_important_text(soup):
    parts = []

    parts.append(soup.get_text(" ", strip=True)[:3000])

    header = soup.find("header")
    if header:
        parts.append(header.get_text(" ", strip=True))

    footer = soup.find("footer")
    if footer:
        parts.append(footer.get_text(" ", strip=True))

    nav = soup.find("nav")
    if nav:
        parts.append(nav.get_text(" ", strip=True))

    return " ".join(parts)

# ================= CATEGORY DETECTION =================
def detect_category(text):
    t = text.lower()

    if any(x in t for x in ["casino","bet","slot","gambling"]):
        return "Casino / Betting"
    if any(x in t for x in ["restaurant","menu","food","pizza","bbq"]):
        return "Restaurant / Food"
    if any(x in t for x in ["shop","cart","buy","product"]):
        return "Ecommerce"
    if any(x in t for x in ["blog","article","author"]):
        return "Blog / Personal"
    if any(x in t for x in ["agency","marketing","services"]):
        return "Business / Agency"
    if any(x in t for x in ["foundation","organization","ngo"]):
        return "Organization"
    
    return "Unknown / Misc"

# ================= FETCH =================
def fetch_html(url, browser=None):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.text
    except:
        if browser:
            try:
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_timeout(2000)
                html = page.content()
                page.close()
                return html
            except:
                return ""
    return ""

# ================= SCRAPER =================
def scrape(url, browser):
    domain = get_domain(url)
    found = set()
    all_text = ""
    visited = set()

    for path in PATHS:
        try:
            full = urljoin(url, path)
            if full in visited:
                continue
            visited.add(full)

            html = fetch_html(full, browser)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")

            # 🔥 RAW EMAIL SCAN
            emails = re.findall(EMAIL_REGEX, html)

            # mailto
            for a in soup.find_all("a", href=True):
                if "mailto:" in a['href']:
                    emails.append(a['href'].replace("mailto:", ""))

            for e in emails:
                e = clean_email(e)
                if is_valid(e):
                    found.add(e)

            # 🔥 IMPORTANT TEXT
            important_text = extract_important_text(soup)
            all_text += " " + important_text

            # 🌍 TRANSLATE
            translated = smart_translate(important_text)

            # 🔥 SCAN AGAIN AFTER TRANSLATION
            emails2 = re.findall(EMAIL_REGEX, translated)

            for e in emails2:
                e = clean_email(e)
                if is_valid(e):
                    found.add(e)

            # 🔥 INTERNAL LINKS (LIMITED)
            for a in soup.find_all("a", href=True):
                link = a['href']
                if domain in link and len(visited) < 6:
                    visited.add(link)
                    html2 = fetch_html(link, browser)
                    if html2:
                        emails3 = re.findall(EMAIL_REGEX, html2)
                        for e in emails3:
                            e = clean_email(e)
                            if is_valid(e):
                                found.add(e)

            if len(found) >= 5:
                break

        except:
            continue

    # ❌ NO EMAIL → CATEGORY
    if not found:
        category = detect_category(all_text)
        return url, [f"No Email | Category: {category}"]

    return url, list(found)[:5]

# ================= RUN =================
if st.button("🚀 Start Scraping"):

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    results = []

    with st.spinner("Scraping like a PRO..."):

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            with ThreadPoolExecutor(max_workers=5) as ex:
                futures = [
                    ex.submit(scrape, u if u.startswith("http") else "https://" + u, browser)
                    for u in urls
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

            browser.close()

    df = pd.DataFrame(results)
    st.session_state.df = df

# ================= OUTPUT =================
if st.session_state.df is not None:

    st.success(f"✅ {len(st.session_state.df)} Websites Processed")
    st.dataframe(st.session_state.df, use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        st.session_state.df.to_csv(index=False),
        "emails.csv"
    )
