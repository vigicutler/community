# EMERGENCY FIX - NO EMOJI IN HTML
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="NYC Volunteer Events", layout="wide")

st.title("🌱 NYC Community Event Agent")
st.write("Choose how you'd like to help and find meaningful events near you")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Merged_Enriched_Events_CLUSTERED.csv")
    return df.fillna("")

df = load_data()
st.success(f"Loaded {len(df)} events!")

# Simple search
query = st.text_input("How can I help?", placeholder="e.g. dogs, kids, environment")

if query:
    mask = df['title'].str.contains(query, case=False, na=False)
    results = df[mask].head(10)
    
    for _, row in results.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(f"**Org:** {row.get('org_title', 'Unknown')}")
        st.markdown(f"**Description:** {row.get('description', 'No description')[:200]}...")
        st.markdown("---")
else:
    st.info("Enter a search term to find volunteer opportunities!")
