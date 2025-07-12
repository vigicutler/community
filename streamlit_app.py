import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="🌱 NYC Volunteer Events",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS - Clean professional design like vigiwater.org
st.markdown("""
<style>
    /* SOLID COLORS ONLY - NO GRADIENTS! */
    :root {
        --dark-olive: #4E5D46;
        --blue: #4E91B3;
        --warm-brown: #8D716D;
        --coral: #D98B73;
        --orange: #FDA767;
    }
    
    /* Clean main app */
    .stApp {
        background-color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* SOLID BLUE header - NO GRADIENT */
    .main-header {
        background-color: var(--blue);
        color: white;
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(78, 145, 179, 0.2);
    }
    
    /* SOLID WHITE search container with warm brown border */
    .search-container {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid var(--warm-brown);
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* SOLID WHITE event cards with coral border */
    .event-card {
        background-color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
        border-left: 5px solid var(--coral);
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .event-title {
        color: var(--dark-olive);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .event-org {
        color: var(--blue);
        font-weight: 500;
        margin-bottom: 0.3rem;
    }
    
    .event-location {
        color: var(--warm-brown);
        font-weight: 500;
        margin-bottom: 0.8rem;
    }
    
    /* SOLID CORAL tags - NO GRADIENT */
    .tag {
        background-color: var(--coral);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.3rem;
        display: inline-block;
    }
    
    /* WHITE inputs with warm brown border */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #212529 !important;
        border: 2px solid var(--warm-brown) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    
    /* NUCLEAR OPTION FOR MAIN AREA DROPDOWNS - OVERRIDE EVERYTHING! */
    .stSelectbox > div > div,
    .stSelectbox > div > div > div,
    .stSelectbox > div > div > div > div,
    .stSelectbox > div > div > div > div > div,
    .stSelectbox select,
    .stSelectbox option {
        background-color: white !important;
        background: white !important;
        color: #000000 !important;
        border: 2px solid var(--warm-brown) !important;
        border-radius: 10px !important;
    }
    
    /* TARGET EVERY POSSIBLE DROPDOWN ELEMENT */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span,
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] span,
    ul[data-baseweb="menu"],
    ul[data-baseweb="menu"] li,
    ul[data-baseweb="menu"] li div,
    ul[data-baseweb="menu"] li span {
        background-color: white !important;
        background: white !important;
        color: #000000 !important;
    }
    
    /* FORCE ALL SELECTBOX COMPONENTS */
    .stSelectbox *,
    .stSelectbox div,
    .stSelectbox span,
    .stSelectbox li,
    .stSelectbox ul {
        background-color: white !important;
        background: white !important;
        color: #000000 !important;
    }
    
    /* OVERRIDE ANY THEME STYLES */
    [data-testid="stSelectbox"] *,
    [data-testid="stSelectbox"] div,
    [data-testid="stSelectbox"] span {
        background-color: white !important;
        background: white !important;
        color: #000000 !important;
    }
    
    /* MAIN AREA ONLY - NOT SIDEBAR */
    .main .stSelectbox *,
    .block-container .stSelectbox *,
    .element-container .stSelectbox * {
        background-color: white !important;
        background: white !important;
        color: #000000 !important;
    }
    
    /* STREAMLIT SELECT WIDGET OVERRIDE */
    .stSelectbox div[role="combobox"],
    .stSelectbox div[role="combobox"] *,
    .stSelectbox div[role="listbox"],
    .stSelectbox div[role="listbox"] *,
    .stSelectbox div[role="option"],
    .stSelectbox div[role="option"] * {
        background-color: white !important;
        background: white !important;
        color: #000000 !important;
    }
    
    /* SOLID ORANGE buttons - NO GRADIENT */
    .stButton > button {
        background-color: var(--orange) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: var(--coral) !important;
    }
    
    /* SOLID BLUE primary button */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: var(--blue) !important;
    }
    
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: var(--dark-olive) !important;
    }
    
    /* DARK OLIVE SIDEBAR with WHITE TEXT - FORCE EVERYTHING WHITE! */
    .css-1d391kg {
        background-color: var(--dark-olive) !important;
    }
    
    /* NUCLEAR OPTION - FORCE ALL SIDEBAR TEXT TO BE WHITE */
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown * {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stText {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] p {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] div {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] span {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4 {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] .stMetric label {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stMetric [data-testid="metric-value"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Legacy sidebar selectors - keep these too */
    .css-1d391kg * {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown * {
        color: white !important;
    }
    
    .css-1d391kg .stText * {
        color: white !important;
    }
    
    .css-1d391kg p {
        color: white !important;
    }
    
    .css-1d391kg div {
        color: white !important;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4 {
        color: white !important;
    }
    
    .css-1d391kg label {
        color: white !important;
        font-weight: 600 !important;
    }
    
    .css-1d391kg .stMetric label {
        color: white !important;
    }
    
    .css-1d391kg .stMetric [data-testid="metric-value"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* WHITE sidebar inputs with dark text - READABLE! */
    .css-1d391kg .stTextInput > div > div > input {
        background-color: white !important;
        color: #212529 !important;
        border: 2px solid var(--coral) !important;
    }
    
    /* NUCLEAR OPTION FOR DROPDOWNS - OVERRIDE EVERYTHING! */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stSelectbox > div > div > div,
    section[data-testid="stSidebar"] .stSelectbox > div > div > div > div,
    section[data-testid="stSidebar"] .stSelectbox select,
    section[data-testid="stSidebar"] .stSelectbox option,
    .css-1d391kg .stSelectbox > div > div,
    .css-1d391kg .stSelectbox > div > div > div,
    .css-1d391kg .stSelectbox > div > div > div > div,
    .css-1d391kg .stSelectbox select,
    .css-1d391kg .stSelectbox option {
        background-color: white !important;
        background: white !important;
        color: #212529 !important;
        border: 2px solid var(--coral) !important;
    }
    
    /* Target dropdown menu specifically */
    section[data-testid="stSidebar"] div[data-baseweb="select"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[data-baseweb="popover"],
    section[data-testid="stSidebar"] div[data-baseweb="popover"] div,
    section[data-testid="stSidebar"] ul[data-baseweb="menu"],
    section[data-testid="stSidebar"] ul[data-baseweb="menu"] li,
    .css-1d391kg div[data-baseweb="select"],
    .css-1d391kg div[data-baseweb="select"] > div,
    .css-1d391kg div[data-baseweb="select"] div,
    .css-1d391kg div[data-baseweb="popover"],
    .css-1d391kg div[data-baseweb="popover"] div,
    .css-1d391kg ul[data-baseweb="menu"],
    .css-1d391kg ul[data-baseweb="menu"] li {
        background-color: white !important;
        background: white !important;
        color: #212529 !important;
    }
    
    /* Target ANY dropdown in sidebar */
    section[data-testid="stSidebar"] .stSelectbox *,
    .css-1d391kg .stSelectbox * {
        background-color: white !important;
        background: white !important;
        color: #212529 !important;
    }
    
    /* Override any dark theme */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] *,
    .css-1d391kg [data-testid="stSelectbox"] * {
        background-color: white !important;
        background: white !important;
        color: #212529 !important;
    }
    
    /* WHITE metrics with coral border */
    div[data-testid="metric-container"] {
        background-color: white !important;
        border-radius: 12px;
        padding: 1.2rem;
        border: 2px solid var(--coral) !important;
        margin-bottom: 1rem !important;
    }
    
    div[data-testid="metric-container"] label {
        color: var(--dark-olive) !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: var(--dark-olive) !important;
        font-weight: 700 !important;
    }
    
    /* ORANGE rating display */
    .rating-display {
        color: var(--orange);
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main content text */
    .stMarkdown, .stText, p, div {
        color: #212529 !important;
    }
    
    label {
        color: #495057 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)
</style>
""", unsafe_allow_html=True)

# Beautiful header with your colors
st.markdown("""
<div class="main-header">
    <h1>🌱 NYC Community Event Agent</h1>
    <p>Choose how you'd like to help and find meaningful events near you</p>
</div>
""", unsafe_allow_html=True)

# === Community Rating System ===
FEEDBACK_CSV = "feedback_backup.csv"

def ensure_feedback_csv():
    if not os.path.exists(FEEDBACK_CSV):
        pd.DataFrame(columns=["event_id", "rating", "comment", "timestamp"]).to_csv(FEEDBACK_CSV, index=False)

def load_feedback():
    if os.path.exists(FEEDBACK_CSV):
        return pd.read_csv(FEEDBACK_CSV)
    return pd.DataFrame(columns=["event_id", "rating", "comment", "timestamp"])

def save_feedback(df):
    df.to_csv(FEEDBACK_CSV, index=False)

def store_feedback(event_id, rating, comment):
    df = load_feedback()
    timestamp = datetime.utcnow().isoformat()
    idx = df[df.event_id == event_id].index
    if len(idx):
        df.loc[idx, ["rating", "comment", "timestamp"]] = [rating, comment, timestamp]
    else:
        new_row = pd.DataFrame([{"event_id": event_id, "rating": rating, "comment": comment, "timestamp": timestamp}])
        df = pd.concat([df, new_row], ignore_index=True)
    save_feedback(df)

def get_event_rating(event_id):
    df = load_feedback()
    ratings = df[df.event_id == event_id]["rating"]
    return round(ratings.mean(), 2) if not ratings.empty else None

ensure_feedback_csv()

# Initialize session state
if 'loaded_data' not in st.session_state:
    st.session_state.loaded_data = None

# Data loading function
def load_volunteer_data():
    """Load and MERGE both of YOUR CSV files for complete data"""
    
    # Load BOTH your CSV files
    enriched_df = pd.read_csv("Merged_Enriched_Events_CLUSTERED.csv")
    historical_df = pd.read_csv("NYC_Service__Volunteer_Opportunities__Historical__20250626.csv")
    
    # Clean both datasets
    enriched_df = enriched_df.fillna("")
    historical_df = historical_df.fillna("")
    
    # Merge them on opportunity_id to get BOTH the enriched data AND the location data
    merged_df = enriched_df.merge(
        historical_df[['opportunity_id', 'locality', 'region', 'Borough', 'Latitude', 'Longitude']], 
        on='opportunity_id', 
        how='left'
    )
    
    # Create proper location field using the REAL location data
    merged_df['location_display'] = merged_df.apply(lambda row: 
        f"{row.get('locality', '')}, {row.get('region', '')}" if row.get('locality') 
        else f"{row.get('Borough', '')}, NY" if row.get('Borough')
        else "New York, NY", axis=1
    )
    
    # Convert key columns to strings
    text_columns = ['title', 'description', 'org_title', 'Topical Theme', 'Mood/Intent', 'location_display']
    for col in text_columns:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].astype(str)
    
    # Create event IDs for ratings
    merged_df['event_id'] = merged_df['opportunity_id'].astype(str) + "_" + merged_df['title'].str[:10]
    
    # Create short description
    merged_df['short_description'] = merged_df['description'].str[:150] + "..."
    
    return merged_df

def create_sample_data():
    """Create sample volunteer data"""
    sample_events = {
        'title': [
            'Community Garden Volunteer',
            'Youth Tutoring Program',
            'Animal Shelter Assistant',
            'Food Bank Helper',
            'Senior Companion',
            'Beach Cleanup Volunteer',
            'Literacy Program Helper',
            'Homeless Shelter Support',
            'Environmental Education',
            'Hospital Volunteer'
        ],
        'description': [
            'Help maintain community gardens in Brooklyn. Plant vegetables, maintain paths, and support local food production.',
            'Tutor elementary and middle school students in math, reading, and science after school programs.',
            'Walk dogs, feed cats, clean kennels, and help with animal adoptions at local ASPCA shelter.',
            'Sort, pack, and distribute food to families in need at City Harvest food bank locations.',
            'Provide companionship and assistance to elderly residents in nursing homes and senior centers.',
            'Join monthly beach cleanups at Coney Island and other NYC beaches. Help protect marine life.',
            'Help adults learn to read and write through one-on-one tutoring and group literacy classes.',
            'Serve meals, provide basic support, and assist with daily operations at homeless shelters.',
            'Teach kids about environmental conservation through hands-on activities and nature walks.',
            'Support patients and families at local hospitals through visitor programs and administrative help.'
        ],
        'org_title': [
            'Brooklyn Community Gardens',
            'NYC Education Alliance',
            'ASPCA NYC',
            'City Harvest',
            'Senior Services Network',
            'NYC Parks Department',
            'Literacy Volunteers of NYC',
            'Coalition for the Homeless',
            'Central Park Conservancy',
            'NewYork-Presbyterian Hospital'
        ],
        'primary_loc': [
            'Brooklyn, NY',
            'Manhattan, NY',
            'Queens, NY',
            'Bronx, NY',
            'Manhattan, NY',
            'Brooklyn, NY',
            'Queens, NY',
            'Manhattan, NY',
            'Manhattan, NY',
            'Manhattan, NY'
        ],
        'Topical Theme': [
            'Environment',
            'Education',
            'Animals',
            'Hunger Relief',
            'Elderly Care',
            'Environment',
            'Education',
            'Homelessness',
            'Environment',
            'Healthcare'
        ],
        'Mood/Intent': [
            'Outdoor Activity',
            'Skill Building',
            'Animal Care',
            'Community Service',
            'Social Connection',
            'Physical Activity',
            'Teaching',
            'Direct Service',
            'Education',
            'Support'
    }
    
    df = pd.DataFrame(sample_events)
    df['short_description'] = df['description'].str[:150] + "..."
    st.info("📋 Using sample volunteer opportunities for demonstration")
    return df

# Load YOUR REAL DATA
with st.spinner("🔄 Loading your volunteer opportunities..."):
    df = load_volunteer_data()

# Search interface with ALL your original filters
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "👋️ How can I help?",
        placeholder="e.g., help kids, environment, animals, food bank, elderly care..."
    )

with col2:
    search_button = st.button("🚀 **Search**", type="primary", use_container_width=True)

# Your original filter options
col1, col2, col3 = st.columns(3)

with col1:
    # Mood/Intent dropdown (your core feature!)
    mood_options = ["(no preference)"]
    if 'Mood/Intent' in df.columns:
        unique_moods = [m for m in df['Mood/Intent'].unique() if m and str(m) != 'nan' and str(m) != '']
        mood_options.extend(sorted(unique_moods))
    mood_input = st.selectbox("Optional — Set an Intention", mood_options)

with col2:
    # ZIP Code filter (your core feature!)
    zipcode_input = st.text_input("Optional — ZIP Code", placeholder="e.g. 10027")

with col3:
    # Weather filter (your core feature!)
    weather_filter = st.selectbox("Filter by Weather Option", ["", "Indoors", "Outdoors", "Flexible"])

# Quick search buttons
st.markdown("**Quick searches:**")
quick_searches = ['Education', 'Environment', 'Animals', 'Hunger Relief', 'Elderly Care', 'Healthcare']
cols = st.columns(len(quick_searches))

for i, topic in enumerate(quick_searches):
    with cols[i]:
        if st.button(topic, key=f"quick_{i}"):
            search_query = topic.lower()
            search_button = True

# Perform search with ALL your filters
if search_button or search_query:
    if search_query:
        # Search logic with your original filtering
        query_lower = search_query.lower()
        
        # Start with all events
        results = df.copy()
        
        # Apply your original filters
        if mood_input != "(no preference)":
            results = results[results['Mood/Intent'].str.contains(mood_input, na=False, case=False)]
        
        if zipcode_input:
            # Filter by ZIP code if Postcode column exists
            if 'Postcode' in results.columns:
                results = results[results['Postcode'].astype(str).str.startswith(zipcode_input, na=False)]
        
        if weather_filter:
            # Filter by weather if Weather Badge column exists
            if 'Weather Badge' in results.columns:
                results = results[results['Weather Badge'].str.contains(weather_filter, na=False, case=False)]
        
        # Text search
        text_mask = (
            results['title'].str.lower().str.contains(query_lower, na=False) |
            results['description'].str.lower().str.contains(query_lower, na=False) |
            results.get('Topical Theme', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False) |
            results.get('Mood/Intent', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False)
        )
        
        results = results[text_mask]
        
        if len(results) == 0:
            # Try individual words if no results
            words = query_lower.split()
            for word in words:
                word_mask = (
                    df['title'].str.lower().str.contains(word, na=False) |
                    df['description'].str.lower().str.contains(word, na=False)
                )
                word_results = df[word_mask]
                
                # Apply filters to word results too
                if mood_input != "(no preference)":
                    word_results = word_results[word_results['Mood/Intent'].str.contains(mood_input, na=False, case=False)]
                if zipcode_input and 'Postcode' in word_results.columns:
                    word_results = word_results[word_results['Postcode'].astype(str).str.startswith(zipcode_input, na=False)]
                if weather_filter and 'Weather Badge' in word_results.columns:
                    word_results = word_results[word_results['Weather Badge'].str.contains(weather_filter, na=False, case=False)]
                
                results = pd.concat([results, word_results]).drop_duplicates()
        
        # Display results
        st.markdown("---")
        if len(results) > 0:
            st.subheader(f"🎯 Found {len(results)} matching opportunities")
            
            # Display each result with beautiful styling
            for idx, (_, event) in enumerate(results.head(15).iterrows()):
                # Beautiful event card
                st.markdown(f"""
                <div class="event-card">
                    <div class="event-title">🌟 {event['title']}</div>
                    <div class="event-org">🏢 {event['org_title']}</div>
                    <div class="event-location">📍 {event['location_display']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Theme and type
                        if 'Topical Theme' in event and event['Topical Theme']:
                            st.markdown(f'<span class="tag">🎯 {event["Topical Theme"]}</span>', unsafe_allow_html=True)
                        
                        if 'Mood/Intent' in event and event['Mood/Intent']:
                            st.markdown(f'<span class="tag">💭 {event["Mood/Intent"]}</span>', unsafe_allow_html=True)
                        
                        # Additional tags
                        for tag_col in ['Effort Estimate', 'Weather Badge']:
                            if tag_col in event and event[tag_col] and str(event[tag_col]) != 'nan':
                                st.markdown(f'<span class="tag">{event[tag_col]}</span>', unsafe_allow_html=True)
                        
                        st.markdown("**📝 Description:**")
                        st.markdown(event.get('short_description', event.get('description', '')[:150] + "..."))
                        
                        # COMMUNITY RATING DISPLAY
                        avg_rating = get_event_rating(event['event_id'])
                        if avg_rating:
                            stars = "⭐" * int(avg_rating)
                            st.markdown(f'<div class="rating-display">{stars} Community Rating: {avg_rating}/5</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**🤝 Get Involved:**")
                        
                        if st.button(f"I'm Interested!", key=f"interest_{idx}"):
                            st.success("🎉 Great! Contact the organization to get started volunteering!")
                        
                        # YOUR ORIGINAL RATING SYSTEM
                        st.markdown("**Rate this event:**")
                        rating = st.slider(
                            "Rating:",
                            1, 5, 3,
                            key=f"rating_{idx}"
                        )
                        
                        comment = st.text_input(
                            "Leave feedback:",
                            key=f"comment_{idx}",
                            placeholder="Optional comment..."
                        )
                        
                        if st.button(f"Submit Feedback", key=f"submit_rating_{idx}"):
                            store_feedback(event['event_id'], rating, comment)
                            st.success("✅ Thanks for the feedback!")
                            st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("🔍 No exact matches found. Try different keywords like 'kids', 'environment', 'food', or 'animals'")
else:
    st.info("Enter a topic like \"food\", \"kids\", \"Inwood\", etc. to explore events.")

# Sidebar with stats, login, and info
with st.sidebar:
    # Fun fake login section
    st.markdown("### Welcome!")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_btn"):
                if username and password:  # Any username/password works!
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Please enter credentials")
        with col2:
            if st.button("Sign Up", key="signup_btn"):
                st.info("Welcome! You're now signed up!")
                st.session_state.logged_in = True
                st.session_state.username = username if username else "New User"
                st.rerun()
    else:
        st.success(f"Welcome back, {st.session_state.get('username', 'User')}!")
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown("---")
    
    st.header("Quick Stats")
    
    total_events = len(df)
    st.metric("Total Opportunities", total_events)
    
    if 'Topical Theme' in df.columns:
        themes = df['Topical Theme'].value_counts()
        if len(themes) > 0:
            top_theme = themes.index[0]
            st.metric("Most Popular Theme", top_theme)
    
    if 'location_display' in df.columns:
        locations = df['location_display'].value_counts()
        if len(locations) > 0:
            top_location = locations.index[0]
            st.metric("Top Location", top_location)
    
    st.markdown("---")
    st.header("Tips")
    st.markdown("""
    **Great search terms:**
    - kids, children, youth
    - environment, green, trees
    - animals, pets, dogs, cats
    - food, hunger, meals
    - elderly, seniors
    - education, tutoring
    - health, hospital
    """)
    
    st.markdown("---")
    st.header("About")
    st.markdown("""
    This app helps you find meaningful volunteer opportunities across New York City. 
    
    Search by cause, location, or organization to discover ways to make a difference in your community!
    """)

# Beautiful footer with your colors
st.markdown("""
<div class="footer">
<h3>🌱 NYC Community Event Agent</h3>
<p><em>Connecting volunteers with meaningful opportunities across New York City</em></p>
<p><strong>Built with love for the community</strong></p>
</div>
""", unsafe_allow_html=True)
    .css-1d391kg [data-testid="stSelectbox"] * {
        background-color: white !important;
        background: white !important;
        color: #212529 !important;
    }
    
    /* WHITE metrics with coral border */
    div[data-testid="metric-container"] {
        background-color: white !important;
        border-radius: 12px;
        padding: 1.2rem;
        border: 2px solid var(--coral) !important;
        margin-bottom: 1rem !important;
    }
    
    div[data-testid="metric-container"] label {
        color: var(--dark-olive) !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: var(--dark-olive) !important;
        font-weight: 700 !important;
    }
    
    /* ORANGE rating display */
    .rating-display {
        color: var(--orange);
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main content text */
    .stMarkdown, .stText, p, div {
        color: #212529 !important;
    }
    
    label {
        color: #495057 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)
</style>
""", unsafe_allow_html=True)

# Beautiful header with your colors
st.markdown("""
<div class="main-header">
    <h1>🌱 NYC Community Event Agent</h1>
    <p>Choose how you'd like to help and find meaningful events near you</p>
</div>
""", unsafe_allow_html=True)

# === Community Rating System ===
FEEDBACK_CSV = "feedback_backup.csv"

def ensure_feedback_csv():
    if not os.path.exists(FEEDBACK_CSV):
        pd.DataFrame(columns=["event_id", "rating", "comment", "timestamp"]).to_csv(FEEDBACK_CSV, index=False)

def load_feedback():
    if os.path.exists(FEEDBACK_CSV):
        return pd.read_csv(FEEDBACK_CSV)
    return pd.DataFrame(columns=["event_id", "rating", "comment", "timestamp"])

def save_feedback(df):
    df.to_csv(FEEDBACK_CSV, index=False)

def store_feedback(event_id, rating, comment):
    df = load_feedback()
    timestamp = datetime.utcnow().isoformat()
    idx = df[df.event_id == event_id].index
    if len(idx):
        df.loc[idx, ["rating", "comment", "timestamp"]] = [rating, comment, timestamp]
    else:
        new_row = pd.DataFrame([{"event_id": event_id, "rating": rating, "comment": comment, "timestamp": timestamp}])
        df = pd.concat([df, new_row], ignore_index=True)
    save_feedback(df)

def get_event_rating(event_id):
    df = load_feedback()
    ratings = df[df.event_id == event_id]["rating"]
    return round(ratings.mean(), 2) if not ratings.empty else None

ensure_feedback_csv()

# Initialize session state
if 'loaded_data' not in st.session_state:
    st.session_state.loaded_data = None

# Data loading function
def load_volunteer_data():
    """Load and MERGE both of YOUR CSV files for complete data"""
    
    # Load BOTH your CSV files
    enriched_df = pd.read_csv("Merged_Enriched_Events_CLUSTERED.csv")
    historical_df = pd.read_csv("NYC_Service__Volunteer_Opportunities__Historical__20250626.csv")
    
    # Clean both datasets
    enriched_df = enriched_df.fillna("")
    historical_df = historical_df.fillna("")
    
    # Merge them on opportunity_id to get BOTH the enriched data AND the location data
    merged_df = enriched_df.merge(
        historical_df[['opportunity_id', 'locality', 'region', 'Borough', 'Latitude', 'Longitude']], 
        on='opportunity_id', 
        how='left'
    )
    
    # Create proper location field using the REAL location data
    merged_df['location_display'] = merged_df.apply(lambda row: 
        f"{row.get('locality', '')}, {row.get('region', '')}" if row.get('locality') 
        else f"{row.get('Borough', '')}, NY" if row.get('Borough')
        else "New York, NY", axis=1
    )
    
    # Convert key columns to strings
    text_columns = ['title', 'description', 'org_title', 'Topical Theme', 'Mood/Intent', 'location_display']
    for col in text_columns:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].astype(str)
    
    # Create event IDs for ratings
    merged_df['event_id'] = merged_df['opportunity_id'].astype(str) + "_" + merged_df['title'].str[:10]
    
    # Create short description
    merged_df['short_description'] = merged_df['description'].str[:150] + "..."
    
    return merged_df

def create_sample_data():
    """Create sample volunteer data"""
    sample_events = {
        'title': [
            'Community Garden Volunteer',
            'Youth Tutoring Program',
            'Animal Shelter Assistant',
            'Food Bank Helper',
            'Senior Companion',
            'Beach Cleanup Volunteer',
            'Literacy Program Helper',
            'Homeless Shelter Support',
            'Environmental Education',
            'Hospital Volunteer'
        ],
        'description': [
            'Help maintain community gardens in Brooklyn. Plant vegetables, maintain paths, and support local food production.',
            'Tutor elementary and middle school students in math, reading, and science after school programs.',
            'Walk dogs, feed cats, clean kennels, and help with animal adoptions at local ASPCA shelter.',
            'Sort, pack, and distribute food to families in need at City Harvest food bank locations.',
            'Provide companionship and assistance to elderly residents in nursing homes and senior centers.',
            'Join monthly beach cleanups at Coney Island and other NYC beaches. Help protect marine life.',
            'Help adults learn to read and write through one-on-one tutoring and group literacy classes.',
            'Serve meals, provide basic support, and assist with daily operations at homeless shelters.',
            'Teach kids about environmental conservation through hands-on activities and nature walks.',
            'Support patients and families at local hospitals through visitor programs and administrative help.'
        ],
        'org_title': [
            'Brooklyn Community Gardens',
            'NYC Education Alliance',
            'ASPCA NYC',
            'City Harvest',
            'Senior Services Network',
            'NYC Parks Department',
            'Literacy Volunteers of NYC',
            'Coalition for the Homeless',
            'Central Park Conservancy',
            'NewYork-Presbyterian Hospital'
        ],
        'primary_loc': [
            'Brooklyn, NY',
            'Manhattan, NY',
            'Queens, NY',
            'Bronx, NY',
            'Manhattan, NY',
            'Brooklyn, NY',
            'Queens, NY',
            'Manhattan, NY',
            'Manhattan, NY',
            'Manhattan, NY'
        ],
        'Topical Theme': [
            'Environment',
            'Education',
            'Animals',
            'Hunger Relief',
            'Elderly Care',
            'Environment',
            'Education',
            'Homelessness',
            'Environment',
            'Healthcare'
        ],
        'Mood/Intent': [
            'Outdoor Activity',
            'Skill Building',
            'Animal Care',
            'Community Service',
            'Social Connection',
            'Physical Activity',
            'Teaching',
            'Direct Service',
            'Education',
            'Support'
    }
    
    df = pd.DataFrame(sample_events)
    df['short_description'] = df['description'].str[:150] + "..."
    st.info("📋 Using sample volunteer opportunities for demonstration")
    return df

# Load YOUR REAL DATA
with st.spinner("🔄 Loading your volunteer opportunities..."):
    df = load_volunteer_data()

# Search interface with ALL your original filters
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "👋️ How can I help?",
        placeholder="e.g., help kids, environment, animals, food bank, elderly care..."
    )

with col2:
    search_button = st.button("🚀 **Search**", type="primary", use_container_width=True)

# Your original filter options
col1, col2, col3 = st.columns(3)

with col1:
    # Mood/Intent dropdown (your core feature!)
    mood_options = ["(no preference)"]
    if 'Mood/Intent' in df.columns:
        unique_moods = [m for m in df['Mood/Intent'].unique() if m and str(m) != 'nan' and str(m) != '']
        mood_options.extend(sorted(unique_moods))
    mood_input = st.selectbox("🌫️ Optional — Set an Intention", mood_options)

with col2:
    # ZIP Code filter (your core feature!)
    zipcode_input = st.text_input("📍 Optional — ZIP Code", placeholder="e.g. 10027")

with col3:
    # Weather filter (your core feature!)
    weather_filter = st.selectbox("☀️ Filter by Weather Option", ["", "Indoors", "Outdoors", "Flexible"])

# Quick search buttons
st.markdown("**Quick searches:**")
quick_searches = ['Education', 'Environment', 'Animals', 'Hunger Relief', 'Elderly Care', 'Healthcare']
cols = st.columns(len(quick_searches))

for i, topic in enumerate(quick_searches):
    with cols[i]:
        if st.button(topic, key=f"quick_{i}"):
            search_query = topic.lower()
            search_button = True

# Perform search with ALL your filters
if search_button or search_query:
    if search_query:
        # Search logic with your original filtering
        query_lower = search_query.lower()
        
        # Start with all events
        results = df.copy()
        
        # Apply your original filters
        if mood_input != "(no preference)":
            results = results[results['Mood/Intent'].str.contains(mood_input, na=False, case=False)]
        
        if zipcode_input:
            # Filter by ZIP code if Postcode column exists
            if 'Postcode' in results.columns:
                results = results[results['Postcode'].astype(str).str.startswith(zipcode_input, na=False)]
        
        if weather_filter:
            # Filter by weather if Weather Badge column exists
            if 'Weather Badge' in results.columns:
                results = results[results['Weather Badge'].str.contains(weather_filter, na=False, case=False)]
        
        # Text search
        text_mask = (
            results['title'].str.lower().str.contains(query_lower, na=False) |
            results['description'].str.lower().str.contains(query_lower, na=False) |
            results.get('Topical Theme', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False) |
            results.get('Mood/Intent', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False)
        )
        
        results = results[text_mask]
        
        if len(results) == 0:
            # Try individual words if no results
            words = query_lower.split()
            for word in words:
                word_mask = (
                    df['title'].str.lower().str.contains(word, na=False) |
                    df['description'].str.lower().str.contains(word, na=False)
                )
                word_results = df[word_mask]
                
                # Apply filters to word results too
                if mood_input != "(no preference)":
                    word_results = word_results[word_results['Mood/Intent'].str.contains(mood_input, na=False, case=False)]
                if zipcode_input and 'Postcode' in word_results.columns:
                    word_results = word_results[word_results['Postcode'].astype(str).str.startswith(zipcode_input, na=False)]
                if weather_filter and 'Weather Badge' in word_results.columns:
                    word_results = word_results[word_results['Weather Badge'].str.contains(weather_filter, na=False, case=False)]
                
                results = pd.concat([results, word_results]).drop_duplicates()
        
        # Display results
        st.markdown("---")
        if len(results) > 0:
            st.subheader(f"🎯 Found {len(results)} matching opportunities")
            
            # Display each result with beautiful styling
            for idx, (_, event) in enumerate(results.head(15).iterrows()):
                # Beautiful event card
                st.markdown(f"""
                <div class="event-card">
                    <div class="event-title">🌟 {event['title']}</div>
                    <div class="event-org">🏢 {event['org_title']}</div>
                    <div class="event-location">📍 {event['location_display']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Theme and type
                        if 'Topical Theme' in event and event['Topical Theme']:
                            st.markdown(f'<span class="tag">🎯 {event["Topical Theme"]}</span>', unsafe_allow_html=True)
                        
                        if 'Mood/Intent' in event and event['Mood/Intent']:
                            st.markdown(f'<span class="tag">💭 {event["Mood/Intent"]}</span>', unsafe_allow_html=True)
                        
                        # Additional tags
                        for tag_col in ['Effort Estimate', 'Weather Badge']:
                            if tag_col in event and event[tag_col] and str(event[tag_col]) != 'nan':
                                st.markdown(f'<span class="tag">{event[tag_col]}</span>', unsafe_allow_html=True)
                        
                        st.markdown("**📝 Description:**")
                        st.markdown(event.get('short_description', event.get('description', '')[:150] + "..."))
                        
                        # COMMUNITY RATING DISPLAY
                        avg_rating = get_event_rating(event['event_id'])
                        if avg_rating:
                            stars = "⭐" * int(avg_rating)
                            st.markdown(f'<div class="rating-display">{stars} Community Rating: {avg_rating}/5</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**🤝 Get Involved:**")
                        
                        if st.button(f"I'm Interested!", key=f"interest_{idx}"):
                            st.success("🎉 Great! Contact the organization to get started volunteering!")
                        
                        # YOUR ORIGINAL RATING SYSTEM
                        st.markdown("**Rate this event:**")
                        rating = st.slider(
                            "Rating:",
                            1, 5, 3,
                            key=f"rating_{idx}"
                        )
                        
                        comment = st.text_input(
                            "Leave feedback:",
                            key=f"comment_{idx}",
                            placeholder="Optional comment..."
                        )
                        
                        if st.button(f"Submit Feedback", key=f"submit_rating_{idx}"):
                            store_feedback(event['event_id'], rating, comment)
                            st.success("✅ Thanks for the feedback!")
                            st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("🔍 No exact matches found. Try different keywords like 'kids', 'environment', 'food', or 'animals'")
else:
    st.info("Enter a topic like \"food\", \"kids\", \"Inwood\", etc. to explore events.")

# Sidebar with stats, login, and info
with st.sidebar:
    # Fun fake login section
    st.markdown("### 👋 Welcome!")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_btn"):
                if username and password:  # Any username/password works!
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Please enter credentials")
        with col2:
            if st.button("Sign Up", key="signup_btn"):
                st.info("Welcome! You're now signed up!")
                st.session_state.logged_in = True
                st.session_state.username = username if username else "New User"
                st.rerun()
    else:
        st.success(f"Welcome back, {st.session_state.get('username', 'User')}!")
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown("---")
    
    st.header("📊 Quick Stats")
    
    total_events = len(df)
    st.metric("Total Opportunities", total_events)
    
    if 'Topical Theme' in df.columns:
        themes = df['Topical Theme'].value_counts()
        if len(themes) > 0:
            top_theme = themes.index[0]
            st.metric("Most Popular Theme", top_theme)
    
    if 'location_display' in df.columns:
        locations = df['location_display'].value_counts()
        if len(locations) > 0:
            top_location = locations.index[0]
            st.metric("Top Location", top_location)
    
    st.markdown("---")
    st.header("💡 Tips")
    st.markdown("""
    **Great search terms:**
    - kids, children, youth
    - environment, green, trees
    - animals, pets, dogs, cats
    - food, hunger, meals
    - elderly, seniors
    - education, tutoring
    - health, hospital
    """)
    
    st.markdown("---")
    st.header("🎯 About")
    st.markdown("""
    This app helps you find meaningful volunteer opportunities across New York City. 
    
    Search by cause, location, or organization to discover ways to make a difference in your community!
    """)

# Beautiful footer with your colors
st.markdown("""
<div class="footer">
<h3>🌱 NYC Community Event Agent</h3>
<p><em>Connecting volunteers with meaningful opportunities across New York City</em></p>
<p><strong>Built with love for the community</strong></p>
</div>
""", unsafe_allow_html=True)
<p><em>Connecting volunteers with meaningful opportunities across New York City</em></p>
<p><strong>Built with love for the community</strong></p>
</div>
""", unsafe_allow_html=True)
