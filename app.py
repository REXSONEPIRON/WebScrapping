# app.py

import streamlit as st
import pandas as pd
from email_scraper import scrape_emails

# Page config
st.set_page_config(page_title="Email Scraper", layout="wide", page_icon="📧")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main > div.block-container {
        max-width: 800px;
        padding: 2rem 3rem;
    }
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4a90e2;
        margin-bottom: 0;
    }
    .subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-top: 0.1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357ABD;
    }
    .email-list {
        font-family: "Courier New", Courier, monospace;
        font-size: 1.1rem;
        background: #f1f5f9;
        border-radius: 8px;
        padding: 1rem;
        max-height: 300px;
        overflow-y: auto;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and description
st.markdown('<h1 class="title">📧 Website Email Scraper</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Enter a website URL to find publicly available email addresses.</p>',
    unsafe_allow_html=True,
)

# Input & controls container
with st.form(key='scraper_form'):
    url_input = st.text_input("🔗 Website URL", placeholder="https://example.com")
    depth = st.slider("Crawling Depth (max pages to crawl)", min_value=1, max_value=2, value=1, help="Increase to crawl more pages but it will take longer.")
    submit_button = st.form_submit_button(label="🔍 Start Scraping")

if submit_button:
    if not url_input.startswith(("http://", "https://")):
        st.error("⚠️ Please enter a valid URL starting with http:// or https://")
    else:
        with st.spinner("⏳ Scraping emails, please wait..."):
            emails = scrape_emails(url_input, max_depth=depth)

        if emails:
            st.success(f"✅ Found {len(emails)} email(s):")
            st.markdown('<div class="email-list">', unsafe_allow_html=True)
            for email in emails:
                st.markdown(f"• {email}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Export to CSV button
            df = pd.DataFrame(emails, columns=["Email"])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Emails as CSV",
                data=csv,
                file_name="emails_found.csv",
                mime="text/csv",
                help="Download all scraped emails as a CSV file",
            )
        else:
            st.warning("⚠️ No emails found on the website.")
