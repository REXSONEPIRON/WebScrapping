import streamlit as st
import pandas as pd
from email_scraper import scrape_emails

st.set_page_config(page_title="Email Scraper", layout="centered")

st.title("📧 Website Email Scraper")
st.markdown("Enter a website domain (like `https://example.com`) to find public email addresses.")

# Input field
url_input = st.text_input("Website URL", placeholder="https://yourdomain.com")

# Max depth selector
depth = st.slider("Crawling Depth", 1, 2, 1)

# Scrape button
if st.button("🔍 Start Scraping"):
    if not url_input.startswith("http"):
        st.error("Please enter a valid URL starting with http or https.")
    else:
        with st.spinner("Scraping in progress..."):
            emails = scrape_emails(url_input, max_depth=depth)

        if emails:
            st.success(f"✅ Found {len(emails)} email(s):")
            st.write(emails)

            # Download button
            df = pd.DataFrame(emails, columns=["Email"])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, "emails_found.csv", "text/csv")
        else:
            st.warning("No emails found.")
