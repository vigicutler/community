import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Page config
st.set_page_config(
    page_title="🌱 NYC Volunteer Events",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS - Clean professional design
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
    
    /* RECOMMENDATION CARDS - Special styling */
    .recommendation-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 2px solid var(--orange);
        box-shadow: 0 4px 15px rgba(253, 167, 103, 0.2);
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
    
    /* SIMILARITY SCORE tag */
    .similarity-tag {
        background-color: var(--orange);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-right: 0.5rem;
        margin-bottom: 0.3rem;
        display: inline-block;
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
    
    /* RECOMMENDATION button styling */
    .recommend-button {
        background-color: var(--orange) !important;
        border: 2px solid var(--coral) !important;
    }
    
    /* ORANGE rating display */
    .rating-display {
        color: var(--orange);
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Similarity score display */
    .similarity-score {
        color: var(--blue);
        font-size: 1.1rem;
        font-weight: bold;
        background-color: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        display: inline-block;
        margin-bottom: 1rem;
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

# Beautiful header
st.markdown("""
<div class="main-header">
    <h1>🌱 NYC Community Event Recommender</h1>
    <p>AI-powered recommendations to find your perfect volunteer opportunity</p>
</div>
""", unsafe_allow_html=True)

# === COSINE SIMILARITY RECOMMENDER SYSTEM ===

# File paths for caching
SIMILARITY_MATRIX_FILE = "similarity_matrix.pkl"
TFIDF_VECTORIZER_FILE = "tfidf_vectorizer.pkl"

@st.cache_data
def load_volunteer_data():
    """Load and prepare volunteer data with enhanced features for similarity"""
    try:
        # Load your clustered data
        df = pd.read_csv("Merged_Enriched_Events_CLUSTERED.csv")
        
        # Try to load historical data for location info
        try:
            historical_df = pd.read_csv("NYC_Service__Volunteer_Opportunities__Historical__20250626.csv")
            df = df.merge(
                historical_df[['opportunity_id', 'locality', 'region', 'Borough', 'Latitude', 'Longitude']], 
                on='opportunity_id', 
                how='left'
            )
        except FileNotFoundError:
            st.warning("Historical location data not found - using enriched data only")
        
        # Clean and prepare data
        df = df.fillna("")
        
        # Create location display
        df['location_display'] = df.apply(lambda row: 
            f"{row.get('locality', '')}, {row.get('region', '')}" if row.get('locality') 
            else f"{row.get('Borough', '')}, NY" if row.get('Borough')
            else "New York, NY", axis=1
        )
        
        # Convert key columns to strings for similarity calculation
        text_columns = ['title', 'description', 'org_title', 'Topical Theme', 'Mood/Intent', 'location_display']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Create combined features for similarity calculation
        df['combined_features'] = (
            df.get('title', '') + ' ' + 
            df.get('description', '') + ' ' + 
            df.get('Topical Theme', '') + ' ' + 
            df.get('Mood/Intent', '') + ' ' + 
            df.get('org_title', '') + ' ' +
            df.get('location_display', '')
        )
        
        # Create event IDs
        df['event_id'] = df.index.astype(str) + "_" + df['title'].str[:10]
        df['short_description'] = df['description'].str[:150] + "..."
        
        return df
        
    except FileNotFoundError:
        st.error("❌ Could not find 'Merged_Enriched_Events_CLUSTERED.csv'. Creating sample data...")
        return create_sample_data()

def create_sample_data():
    """Create sample data with proper features for testing"""
    sample_events = {
        'title': [
            'Community Garden Volunteer', 'Youth Tutoring Program', 'Animal Shelter Assistant',
            'Food Bank Helper', 'Senior Companion', 'Beach Cleanup Volunteer',
            'Literacy Program Helper', 'Homeless Shelter Support', 'Environmental Education',
            'Hospital Volunteer', 'Urban Farm Assistant', 'Children Reading Program'
        ],
        'description': [
            'Help maintain community gardens in Brooklyn. Plant vegetables, maintain paths.',
            'Tutor elementary and middle school students in math, reading, and science.',
            'Walk dogs, feed cats, clean kennels, and help with animal adoptions.',
            'Sort, pack, and distribute food to families in need at food banks.',
            'Provide companionship and assistance to elderly residents in nursing homes.',
            'Join monthly beach cleanups at Coney Island and other NYC beaches.',
            'Help adults learn to read and write through tutoring and literacy classes.',
            'Serve meals, provide basic support, and assist with daily operations.',
            'Teach kids about environmental conservation through hands-on activities.',
            'Support patients and families at local hospitals through visitor programs.',
            'Work on sustainable urban farming projects in local communities.',
            'Read to children and help with early literacy development programs.'
        ],
        'org_title': [
            'Brooklyn Community Gardens', 'NYC Education Alliance', 'ASPCA NYC',
            'City Harvest', 'Senior Services Network', 'NYC Parks Department',
            'Literacy Volunteers of NYC', 'Coalition for the Homeless', 'Central Park Conservancy',
            'NewYork-Presbyterian Hospital', 'Brooklyn Urban Farm', 'Children\'s Library Initiative'
        ],
        'location_display': [
            'Brooklyn, NY', 'Manhattan, NY', 'Queens, NY', 'Bronx, NY', 'Manhattan, NY', 'Brooklyn, NY',
            'Queens, NY', 'Manhattan, NY', 'Manhattan, NY', 'Manhattan, NY', 'Brooklyn, NY', 'Bronx, NY'
        ],
        'Topical Theme': [
            'Environment', 'Education', 'Animals', 'Hunger Relief', 'Elderly Care', 'Environment',
            'Education', 'Homelessness', 'Environment', 'Healthcare', 'Environment', 'Education'
        ],
        'Mood/Intent': [
            'Outdoor Activity', 'Skill Building', 'Animal Care', 'Community Service', 'Social Connection',
            'Physical Activity', 'Teaching', 'Direct Service', 'Education', 'Support', 'Outdoor Activity', 'Teaching'
        ]
    }
    
    df = pd.DataFrame(sample_events)
    df['combined_features'] = (df['title'] + ' ' + df['description'] + ' ' + 
                              df['Topical Theme'] + ' ' + df['Mood/Intent'])
    df['event_id'] = df.index.astype(str) + "_" + df['title'].str[:10]
    df['short_description'] = df['description'].str[:150] + "..."
    
    st.info("📋 Using sample volunteer opportunities for demonstration")
    return df

@st.cache_data
def create_similarity_matrix(df):
    """Create cosine similarity matrix for all events"""
    try:
        # Load cached similarity matrix if exists
        if os.path.exists(SIMILARITY_MATRIX_FILE) and os.path.exists(TFIDF_VECTORIZER_FILE):
            with open(SIMILARITY_MATRIX_FILE, 'rb') as f:
                similarity_matrix = pickle.load(f)
            with open(TFIDF_VECTORIZER_FILE, 'rb') as f:
                tfidf_vectorizer = pickle.load(f)
            st.success("✅ Loaded cached similarity matrix")
            return similarity_matrix, tfidf_vectorizer
    except Exception as e:
        st.warning(f"Could not load cached similarity matrix: {e}")
    
    # Create new similarity matrix
    with st.spinner("🔄 Computing cosine similarity matrix for all events..."):
        # Create TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)  # Include bigrams for better context
        )
        
        # Fit and transform the combined features
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_features'])
        
        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Cache the results
        try:
            with open(SIMILARITY_MATRIX_FILE, 'wb') as f:
                pickle.dump(similarity_matrix, f)
            with open(TFIDF_VECTORIZER_FILE, 'wb') as f:
                pickle.dump(tfidf_vectorizer, f)
            st.success("✅ Similarity matrix computed and cached!")
        except Exception as e:
            st.warning(f"Could not cache similarity matrix: {e}")
    
    return similarity_matrix, tfidf_vectorizer

def get_event_recommendations(event_index, similarity_matrix, df, num_recommendations=5):
    """Get similar events using cosine similarity"""
    if event_index >= len(similarity_matrix):
        return pd.DataFrame()
    
    # Get similarity scores for this event
    sim_scores = list(enumerate(similarity_matrix[event_index]))
    
    # Sort by similarity score (excluding the event itself)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]
    
    # Get top N similar events
    top_similar = sim_scores[:num_recommendations]
    
    # Get event indices and similarity scores
    event_indices = [i[0] for i in top_similar]
    similarity_scores = [i[1] for i in top_similar]
    
    # Return similar events with similarity scores
    similar_events = df.iloc[event_indices].copy()
    similar_events['similarity_score'] = similarity_scores
    
    return similar_events

def get_recommendations_by_preferences(user_themes, user_moods, df, similarity_matrix, num_recommendations=8):
    """Get recommendations based on user's preferred themes and moods"""
    # Create a synthetic user profile
    user_profile = " ".join(user_themes + user_moods)
    
    # Transform user profile using the same vectorizer
    user_tfidf = tfidf_vectorizer.transform([user_profile])
    
    # Calculate similarity between user profile and all events
    user_similarity = cosine_similarity(user_tfidf, tfidf_vectorizer.transform(df['combined_features']))[0]
    
    # Get top recommendations
    sim_scores = list(enumerate(user_similarity))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get top N events
    top_events = sim_scores[:num_recommendations]
    event_indices = [i[0] for i in top_events]
    similarity_scores = [i[1] for i in top_events]
    
    recommended_events = df.iloc[event_indices].copy()
    recommended_events['similarity_score'] = similarity_scores
    
    return recommended_events

# === Community Rating System ===
FEEDBACK_CSV = "feedback_backup.csv"

def ensure_feedback_csv():
    if not os.path.exists(FEEDBACK_CSV):
        pd.DataFrame(columns=["event_id", "rating", "comment", "timestamp"]).to_csv(FEEDBACK_CSV, index=False)

def load_feedback():
    if os.path.exists(FEEDBACK_CSV):
        return pd.read_csv(FEEDBACK_CSV)
    return pd.DataFrame(columns=["event_id", "rating", "comment", "timestamp"])

def store_feedback(event_id, rating, comment):
    df = load_feedback()
    timestamp = datetime.utcnow().isoformat()
    idx = df[df.event_id == event_id].index
    if len(idx):
        df.loc[idx, ["rating", "comment", "timestamp"]] = [rating, comment, timestamp]
    else:
        new_row = pd.DataFrame([{"event_id": event_id, "rating": rating, "comment": comment, "timestamp": timestamp}])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FEEDBACK_CSV, index=False)

def get_event_rating(event_id):
    df = load_feedback()
    ratings = df[df.event_id == event_id]["rating"]
    return round(ratings.mean(), 2) if not ratings.empty else None

ensure_feedback_csv()

# === MAIN APP ===

# Load data and create similarity matrix
df = load_volunteer_data()
similarity_matrix, tfidf_vectorizer = create_similarity_matrix(df)

# Initialize session state
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {'themes': [], 'moods': []}
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False
if 'recommended_for_event' not in st.session_state:
    st.session_state.recommended_for_event = None

# Main navigation
tab1, tab2, tab3 = st.tabs(["🔍 Search Events", "🎯 Get Recommendations", "⭐ My Interests"])

with tab1:
    st.subheader("Search Volunteer Opportunities")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "What kind of volunteer work interests you?",
            placeholder="e.g., help kids, environment, animals, food bank..."
        )
    
    with col2:
        search_button = st.button("🚀 Search", type="primary", use_container_width=True)
    
    # Quick search buttons
    st.markdown("**Quick searches:**")
    quick_searches = ['Education', 'Environment', 'Animals', 'Hunger Relief', 'Elderly Care', 'Healthcare']
    cols = st.columns(len(quick_searches))
    
    for i, topic in enumerate(quick_searches):
        with cols[i]:
            if st.button(topic, key=f"quick_{i}"):
                search_query = topic.lower()
                search_button = True
    
    # Perform search
    if search_button or search_query:
        if search_query:
            query_lower = search_query.lower()
            
            # Search logic
            text_mask = (
                df['title'].str.lower().str.contains(query_lower, na=False) |
                df['description'].str.lower().str.contains(query_lower, na=False) |
                df.get('Topical Theme', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False) |
                df.get('Mood/Intent', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False)
            )
            
            results = df[text_mask]
            
            if len(results) == 0:
                # Fallback search
                words = query_lower.split()
                for word in words:
                    word_mask = (
                        df['title'].str.lower().str.contains(word, na=False) |
                        df['description'].str.lower().str.contains(word, na=False)
                    )
                    word_results = df[word_mask]
                    results = pd.concat([results, word_results]).drop_duplicates()
            
            # Display results
            if len(results) > 0:
                st.markdown(f"### 🎯 Found {len(results)} matching opportunities")
                
                for idx, (_, event) in enumerate(results.head(10).iterrows()):
                    # Event card
                    st.markdown(f"""
                    <div class="event-card">
                        <div class="event-title">🌟 {event['title']}</div>
                        <div class="event-org">🏢 {event['org_title']}</div>
                        <div class="event-location">📍 {event['location_display']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Tags
                        if 'Topical Theme' in event and event['Topical Theme']:
                            st.markdown(f'<span class="tag">🎯 {event["Topical Theme"]}</span>', unsafe_allow_html=True)
                        
                        if 'Mood/Intent' in event and event['Mood/Intent']:
                            st.markdown(f'<span class="tag">💭 {event["Mood/Intent"]}</span>', unsafe_allow_html=True)
                        
                        st.markdown("**📝 Description:**")
                        st.markdown(event.get('short_description', event.get('description', '')[:150] + "..."))
                        
                        # Community rating
                        avg_rating = get_event_rating(event['event_id'])
                        if avg_rating:
                            stars = "⭐" * int(avg_rating)
                            st.markdown(f'<div class="rating-display">{stars} Rating: {avg_rating}/5</div>', unsafe_allow_html=True)
                    
                    with col2:
                        # Main buttons
                        if st.button(f"I'm Interested!", key=f"interest_{idx}"):
                            st.success("🎉 Great! We'll use this to improve your recommendations!")
                            # Add to user preferences
                            if event['Topical Theme'] not in st.session_state.user_preferences['themes']:
                                st.session_state.user_preferences['themes'].append(event['Topical Theme'])
                            if event['Mood/Intent'] not in st.session_state.user_preferences['moods']:
                                st.session_state.user_preferences['moods'].append(event['Mood/Intent'])
                        
                        # COSINE SIMILARITY RECOMMENDATION BUTTON
                        if st.button(f"🎯 Find Similar Events", key=f"similar_{idx}"):
                            event_index = results.index[idx]
                            st.session_state.show_recommendations = True
                            st.session_state.recommended_for_event = event_index
                            st.rerun()
                        
                        # Rating system
                        rating = st.slider("Rate:", 1, 5, 3, key=f"rating_{idx}")
                        if st.button(f"Submit Rating", key=f"submit_{idx}"):
                            store_feedback(event['event_id'], rating, "")
                            st.success("✅ Thanks!")
                
                # Show recommendations if requested
                if st.session_state.show_recommendations and st.session_state.recommended_for_event is not None:
                    st.markdown("---")
                    st.markdown("### 🎯 Similar Events Recommended For You")
                    
                    similar_events = get_event_recommendations(
                        st.session_state.recommended_for_event, 
                        similarity_matrix, 
                        df, 
                        num_recommendations=5
                    )
                    
                    if not similar_events.empty:
                        for idx, (_, event) in enumerate(similar_events.iterrows()):
                            similarity_score = event['similarity_score']
                            
                            st.markdown(f"""
                            <div class="recommendation-card">
                                <div class="event-title">⭐ {event['title']}</div>
                                <div class="event-org">🏢 {event['org_title']}</div>
                                <div class="event-location">📍 {event['location_display']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f'<div class="similarity-score">🎯 {similarity_score:.2f} similarity match</div>', unsafe_allow_html=True)
                                
                                if 'Topical Theme' in event and event['Topical Theme']:
                                    st.markdown(f'<span class="tag">🎯 {event["Topical Theme"]}</span>', unsafe_allow_html=True)
                                
                                st.markdown(event.get('short_description', event.get('description', '')[:150] + "..."))
                            
                            with col2:
                                if st.button(f"I'm Interested!", key=f"rec_interest_{idx}"):
                                    st.success("🎉 Added to your interests!")
                    
                    if st.button("🔄 Hide Recommendations"):
                        st.session_state.show_recommendations = False
                        st.session_state.recommended_for_event = None
                        st.rerun()
                        
            else:
                st.info("🔍 No matches found. Try different keywords or use the recommendations tab!")

with tab2:
    st.subheader("🎯 Personalized Recommendations")
    st.markdown("Get AI-powered recommendations based on your interests!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Select your interests:**")
        available_themes = df['Topical Theme'].dropna().unique()
        selected_themes = st.multiselect("Choose themes that interest you:", available_themes)
    
    with col2:
        st.markdown("**How do you like to help?**")
        available_moods = df['Mood/Intent'].dropna().unique()
        selected_moods = st.multiselect("Choose your preferred volunteer style:", available_moods)
    
    if st.button("🚀 Get My Recommendations", type="primary"):
        if selected_themes or selected_moods:
            recommendations = get_recommendations_by_preferences(
                selected_themes, selected_moods, df, similarity_matrix, num_recommendations=6
            )
            
            st.markdown("### 🌟 Your Personalized Recommendations")
            
            for idx, (_, event) in enumerate(recommendations.iterrows()):
                similarity_score = event['similarity_score']
                
                st.markdown(f"""
                <div class="recommendation-card">
                    <div class="event-title">⭐ {event['title']}</div>
                    <div class="event-org">🏢 {event['org_title']}</div>
                    <div class="event-location">📍 {event['location_display']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f'<div class="similarity-score">🎯 {similarity_score:.2f} match score</div>', unsafe_allow_html=True)
                    
                    if 'Topical Theme' in event and event['Topical Theme']:
                        st.markdown(f'<span class="tag">🎯 {event["Topical Theme"]}</span>', unsafe_allow_html=True)
                    
                    if 'Mood/Intent' in event and event['Mood/Intent']:
                        st.markdown(f'<span class="tag">💭 {event["Mood/Intent"]}</span>', unsafe_allow_html=True)
                    
                    st.markdown(event.get('short_description', event.get('description', '')[:150] + "..."))
                
                with col2:
                    if st.button(f"I'm Interested!", key=f"pref_interest_{idx}"):
                        st.success("🎉 Great choice!")
        else:
            st.warning("Please select at least one theme or mood to get recommendations!")

with tab3:
    st.subheader("⭐ Your Volunteer Interests")
    
    if st.session_state.user_preferences['themes'] or st.session_state.user_preferences['moods']:
        st.markdown("**Your preferred themes:**")
        for theme in st.session_state.user_preferences['themes']:
            st.markdown(f"• {theme}")
        
        st.markdown("**Your preferred volunteer styles:**")
        for mood in st.session_state.user_preferences['moods']:
            st.markdown(f"• {mood}")
        
        if st.button("🔄 Clear My Preferences"):
            st.session_state.user_preferences = {'themes': [], 'moods': []}
            st.success("Preferences cleared!")
            st.rerun()
    else:
        st.info("Start exploring events and clicking 'I'm Interested!' to build your preference profile!")

# Sidebar with stats
with st.sidebar:
    st.header("📊 Recommendation Stats")
    
    total_events = len(df)
    st.metric("Total Opportunities", total_events)
    
    # Show similarity matrix info
    if similarity_matrix is not None:
        st.metric("Similarity Calculations", f"{similarity_matrix.shape[0]}×{similarity_matrix.shape[1]}")
    
    st.markdown("---")
    st.header("🤖 How It Works")
    st.markdown("""
    **This app uses AI to find perfect matches:**
    
    1. **Cosine Similarity** - Mathematically compares events based on content
    2. **TF-IDF Vectorization** - Converts text to numerical vectors
    3. **Personalized Matching** - Learns your preferences over time
    
    The more you interact, the better your recommendations become!
    """)
    
    st.markdown("---")
    st.markdown("**🌱 Built with cosine similarity and machine learning**")
