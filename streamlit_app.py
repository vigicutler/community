import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import os
import json
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import plotly.express as px
import plotly.graph_objects as go

# Configuration
FEEDBACK_CSV = "feedback_data.csv"
USER_PREFERENCES_JSON = "user_preferences.json"

st.set_page_config(
    page_title="🌱 NYC Community Event Agent",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .event-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    .rating-stars {
        color: #ffd700;
        font-size: 1.2em;
    }
    .tag {
        background: #e3f2fd;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🌱 NYC Community Event Agent</h1>
    <p>Find meaningful volunteer opportunities that match your passion and schedule</p>
</div>
""", unsafe_allow_html=True)

# === Enhanced Synonym Mapping ===
COMPREHENSIVE_SYNONYMS = {
    "kids": ["youth", "children", "students", "tutoring", "mentoring", "education", "school"],
    "environment": ["tree", "planting", "gardening", "green", "sustainability", "climate", "nature"],
    "homelessness": ["shelter", "housing", "unsheltered", "support", "food bank", "soup kitchen"],
    "elderly": ["seniors", "older adults", "companionship", "nursing home", "retirement"],
    "animals": ["pets", "rescue", "dogs", "cats", "shelters", "wildlife", "veterinary"],
    "health": ["medical", "healthcare", "hospital", "clinic", "wellness", "mental health"],
    "arts": ["music", "theater", "painting", "creative", "cultural", "museum", "gallery"],
    "sports": ["fitness", "athletic", "recreation", "coaching", "physical activity"],
    "food": ["hunger", "nutrition", "cooking", "meals", "pantry", "kitchen"]
}

# === Data Loading with Error Handling ===
@st.cache_data
def load_event_data():
    """Load and process event data with comprehensive error handling"""
    try:
        # Try to load the main CSV file
        df = pd.read_csv("Merged_Enriched_Events_CLUSTERED.csv")
        
        # Clean and standardize data
        df = df.fillna("")
        
        # Ensure required columns exist with fallbacks
        required_columns = {
            'title': 'title',
            'description': 'description',
            'org_title': 'organization',
            'start_date_date': 'date',
            'primary_loc': 'location'
        }
        
        for required, fallback in required_columns.items():
            if required not in df.columns and fallback in df.columns:
                df[required] = df[fallback]
            elif required not in df.columns:
                df[required] = "Not specified"
        
        # Convert all text columns to strings
        text_columns = ['title', 'description', 'org_title', 'primary_loc']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).replace('nan', '').replace('None', '')
        
        # Create derived columns
        df['short_description'] = df['description'].str[:150] + "..."
        df['search_text'] = (
            df['title'] + " " + 
            df['description'] + " " + 
            df.get('Topical Theme', '') + " " + 
            df.get('Activity Type', '') + " " + 
            df.get('Mood/Intent', '')
        ).str.lower()
        
        # Create unique event IDs
        df['event_id'] = [f"event_{i}_{hash(str(row['title']) + str(row['description']))}" 
                         for i, (_, row) in enumerate(df.iterrows())]
        
        # Clean dates and add time-based features
        if 'start_date_date' in df.columns:
            df['start_date_clean'] = pd.to_datetime(df['start_date_date'], errors='coerce')
            df['is_upcoming'] = df['start_date_clean'] >= datetime.now()
            df['days_until'] = (df['start_date_clean'] - datetime.now()).dt.days
        
        return df
        
    except FileNotFoundError:
        st.error("📁 CSV file not found. Please upload 'Merged_Enriched_Events_CLUSTERED.csv'")
        return create_sample_data()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration"""
    sample_data = {
        'title': [
            'Community Garden Volunteer',
            'Youth Tutoring Program',
            'Animal Shelter Helper',
            'Food Bank Assistant',
            'Senior Companion Program'
        ],
        'description': [
            'Help maintain community gardens in Brooklyn',
            'Tutor elementary school students in math and reading',
            'Walk dogs and care for cats at local animal shelter',
            'Sort and distribute food at community food bank',
            'Provide companionship to elderly residents'
        ],
        'org_title': [
            'Brooklyn Community Gardens',
            'NYC Education Alliance',
            'ASPCA NYC',
            'City Harvest',
            'Senior Services Network'
        ],
        'start_date_date': [
            '2024-08-15',
            '2024-08-20',
            '2024-08-18',
            '2024-08-22',
            '2024-08-25'
        ],
        'primary_loc': [
            'Brooklyn, NY',
            'Manhattan, NY',
            'Queens, NY',
            'Bronx, NY',
            'Manhattan, NY'
        ],
        'Topical Theme': [
            'Environment',
            'Education',
            'Animals',
            'Hunger',
            'Elderly Care'
        ],
        'Mood/Intent': [
            'Outdoor Activity',
            'Skill Building',
            'Animal Care',
            'Community Service',
            'Social Connection'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df['short_description'] = df['description']
    df['search_text'] = (df['title'] + " " + df['description']).str.lower()
    df['event_id'] = [f"sample_{i}" for i in range(len(df))]
    
    return df

# Load data
events_df = load_event_data()
st.success(f"✅ Loaded {len(events_df)} volunteer opportunities!")

# === Advanced Search and Recommendation Engine ===
@st.cache_resource
def load_embeddings_model():
    """Load sentence transformer for semantic search"""
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        st.warning(f"Could not load advanced search model: {e}")
        return None

embedder = load_embeddings_model()

@st.cache_data
def compute_embeddings(texts):
    """Compute embeddings for semantic search"""
    if embedder is None:
        return None
    try:
        return embedder.encode(texts.tolist())
    except Exception as e:
        st.warning(f"Could not compute embeddings: {e}")
        return None

# Compute embeddings for events
event_embeddings = compute_embeddings(events_df['search_text']) if embedder else None

# === User Feedback System ===
def load_feedback_data():
    """Load user feedback from CSV"""
    try:
        if os.path.exists(FEEDBACK_CSV):
            return pd.read_csv(FEEDBACK_CSV)
        else:
            return pd.DataFrame(columns=['event_id', 'rating', 'comment', 'timestamp', 'user_id'])
    except Exception as e:
        st.warning(f"Could not load feedback: {e}")
        return pd.DataFrame(columns=['event_id', 'rating', 'comment', 'timestamp', 'user_id'])

def save_feedback(event_id, rating, comment, user_id="anonymous"):
    """Save user feedback"""
    try:
        feedback_df = load_feedback_data()
        new_feedback = pd.DataFrame([{
            'event_id': event_id,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }])
        
        feedback_df = pd.concat([feedback_df, new_feedback], ignore_index=True)
        feedback_df.to_csv(FEEDBACK_CSV, index=False)
        return True
    except Exception as e:
        st.error(f"Could not save feedback: {e}")
        return False

def get_event_rating(event_id):
    """Get average rating for an event"""
    try:
        feedback_df = load_feedback_data()
        event_feedback = feedback_df[feedback_df['event_id'] == event_id]
        if len(event_feedback) > 0:
            return round(event_feedback['rating'].mean(), 1), len(event_feedback)
        return None, 0
    except:
        return None, 0

# === Advanced Search Function ===
def advanced_search(query, filters, user_preferences=None):
    """Advanced search with multiple ranking factors"""
    
    # Start with all events
    results = events_df.copy()
    
    # Apply filters
    if filters.get('location'):
        results = results[results['primary_loc'].str.contains(filters['location'], case=False, na=False)]
    
    if filters.get('theme') and filters['theme'] != 'Any':
        results = results[results['Topical Theme'].str.contains(filters['theme'], case=False, na=False)]
    
    if filters.get('mood') and filters['mood'] != 'Any':
        results = results[results['Mood/Intent'].str.contains(filters['mood'], case=False, na=False)]
    
    if filters.get('upcoming_only'):
        if 'is_upcoming' in results.columns:
            results = results[results['is_upcoming'] == True]
    
    # Expand query with synonyms
    expanded_query = query.lower()
    for keyword, synonyms in COMPREHENSIVE_SYNONYMS.items():
        if keyword in query.lower():
            expanded_query += " " + " ".join(synonyms)
    
    # Calculate scores
    results['relevance_score'] = 0
    
    # Text matching score
    for idx, row in results.iterrows():
        text_score = 0
        search_text = row['search_text'].lower()
        
        # Exact phrase matching (highest weight)
        if query.lower() in search_text:
            text_score += 10
        
        # Individual word matching
        query_words = expanded_query.split()
        for word in query_words:
            if word in search_text:
                text_score += 1
        
        results.at[idx, 'relevance_score'] += text_score
    
    # Semantic similarity (if available)
    if embedder and event_embeddings is not None:
        try:
            query_embedding = embedder.encode([expanded_query])
            similarities = cosine_similarity(query_embedding, event_embeddings)[0]
            
            # Add semantic scores to filtered results
            filtered_indices = results.index.tolist()
            for i, idx in enumerate(filtered_indices):
                if idx < len(similarities):
                    results.at[idx, 'relevance_score'] += similarities[idx] * 5
        except Exception as e:
            st.warning(f"Could not compute semantic similarity: {e}")
    
    # User preference boost
    if user_preferences:
        for idx, row in results.iterrows():
            pref_score = 0
            
            # Boost based on preferred themes
            if 'preferred_themes' in user_preferences:
                for theme in user_preferences['preferred_themes']:
                    if theme.lower() in row['search_text'].lower():
                        pref_score += 2
            
            # Boost based on preferred locations
            if 'preferred_locations' in user_preferences:
                for location in user_preferences['preferred_locations']:
                    if location.lower() in str(row['primary_loc']).lower():
                        pref_score += 1
            
            results.at[idx, 'relevance_score'] += pref_score
    
    # Rating boost
    feedback_df = load_feedback_data()
    for idx, row in results.iterrows():
        avg_rating, num_ratings = get_event_rating(row['event_id'])
        if avg_rating:
            # Boost score based on rating and number of reviews
            rating_boost = (avg_rating - 3) * 0.5 + min(num_ratings * 0.1, 1)
            results.at[idx, 'relevance_score'] += rating_boost
    
    # Sort by relevance score
    results = results.sort_values('relevance_score', ascending=False)
    
    return results

# === Sidebar: User Profile and Preferences ===
with st.sidebar:
    st.header("🎯 Your Profile")
    
    # User preferences
    with st.expander("Set Your Preferences", expanded=True):
        preferred_themes = st.multiselect(
            "Preferred Causes:",
            options=['Environment', 'Education', 'Health', 'Animals', 'Seniors', 'Youth', 'Arts', 'Sports'],
            default=st.session_state.user_profile.get('preferred_themes', [])
        )
        
        preferred_locations = st.multiselect(
            "Preferred Areas:",
            options=['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'],
            default=st.session_state.user_profile.get('preferred_locations', [])
        )
        
        availability = st.selectbox(
            "Availability:",
            options=['Weekends only', 'Weekdays only', 'Evenings', 'Flexible'],
            index=0
        )
        
        commitment_level = st.selectbox(
            "Commitment Level:",
            options=['One-time events', 'Weekly commitment', 'Monthly commitment', 'Ongoing'],
            index=0
        )
    
    # Update user profile
    st.session_state.user_profile.update({
        'preferred_themes': preferred_themes,
        'preferred_locations': preferred_locations,
        'availability': availability,
        'commitment_level': commitment_level
    })
    
    # Search History
    if st.session_state.search_history:
        st.subheader("🕐 Recent Searches")
        for search in st.session_state.search_history[-5:]:
            if st.button(f"🔍 {search}", key=f"history_{search}"):
                st.session_state.current_query = search

# === Main Search Interface ===
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Find Your Perfect Volunteer Opportunity")
    
    # Main search
    query = st.text_input(
        "What cause do you want to support?",
        placeholder="e.g., help kids learn, clean environment, support elderly...",
        value=st.session_state.get('current_query', '')
    )

with col2:
    st.subheader("🎛️ Filters")
    
    # Search filters
    location_filter = st.selectbox("Location:", ['Any'] + ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'])
    theme_filter = st.selectbox("Theme:", ['Any'] + events_df['Topical Theme'].dropna().unique().tolist())
    mood_filter = st.selectbox("Mood:", ['Any'] + events_df['Mood/Intent'].dropna().unique().tolist())
    upcoming_only = st.checkbox("Upcoming events only", value=True)

# Search execution
if st.button("🚀 Find Opportunities", type="primary") or query:
    if query:
        # Add to search history
        if query not in st.session_state.search_history:
            st.session_state.search_history.append(query)
        
        # Prepare filters
        filters = {
            'location': location_filter if location_filter != 'Any' else '',
            'theme': theme_filter if theme_filter != 'Any' else '',
            'mood': mood_filter if mood_filter != 'Any' else '',
            'upcoming_only': upcoming_only
        }
        
        # Perform search
        with st.spinner("🔍 Finding the perfect opportunities for you..."):
            results = advanced_search(query, filters, st.session_state.user_profile)
            st.session_state.search_results = results
    else:
        st.warning("Please enter what you'd like to volunteer for!")

# === Results Display ===
if st.session_state.search_results is not None and len(st.session_state.search_results) > 0:
    results = st.session_state.search_results
    
    st.markdown("---")
    st.subheader(f"🎯 Found {len(results)} Perfect Matches")
    
    # Display top results
    for idx, (_, event) in enumerate(results.head(10).iterrows()):
        with st.container():
            # Event card
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### 🌟 {event['title']}")
                st.markdown(f"**🏢 {event['org_title']}**")
                st.markdown(f"📅 {event.get('start_date_date', 'Date TBD')}")
                st.markdown(f"📍 {event['primary_loc']}")
                
                # Tags
                tags = []
                if event.get('Topical Theme'):
                    tags.append(f"🎯 {event['Topical Theme']}")
                if event.get('Mood/Intent'):
                    tags.append(f"💭 {event['Mood/Intent']}")
                
                if tags:
                    st.markdown(" ".join([f"`{tag}`" for tag in tags]))
                
                st.markdown(event['short_description'])
            
            with col2:
                # Rating display
                avg_rating, num_ratings = get_event_rating(event['event_id'])
                if avg_rating:
                    stars = "⭐" * int(avg_rating)
                    st.markdown(f"**Rating:** {stars} ({avg_rating}/5)")
                    st.markdown(f"*{num_ratings} reviews*")
                else:
                    st.markdown("*No ratings yet*")
                
                # Relevance score
                st.markdown(f"**Match:** {event.get('relevance_score', 0):.1f}/10")
            
            with col3:
                # Feedback form
                with st.expander("Rate & Review"):
                    rating = st.slider(
                        "Your Rating:",
                        1, 5, 3,
                        key=f"rating_{event['event_id']}_{idx}"
                    )
                    
                    comment = st.text_area(
                        "Comment:",
                        placeholder="Share your experience...",
                        key=f"comment_{event['event_id']}_{idx}"
                    )
                    
                    if st.button(
                        "Submit Review",
                        key=f"submit_{event['event_id']}_{idx}"
                    ):
                        if save_feedback(event['event_id'], rating, comment):
                            st.success("✅ Thank you for your feedback!")
                            st.rerun()
                        else:
                            st.error("❌ Could not save feedback")
            
            st.markdown("---")

elif st.session_state.search_results is not None:
    st.info("🔍 No events found matching your criteria. Try different keywords or filters!")

else:
    # Default view - show featured opportunities
    st.subheader("🌟 Featured Volunteer Opportunities")
    
    featured_events = events_df.head(5)
    for idx, (_, event) in enumerate(featured_events.iterrows()):
        with st.expander(f"🌟 {event['title']} - {event['org_title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(event['description'])
                st.markdown(f"📅 **Date:** {event.get('start_date_date', 'TBD')}")
                st.markdown(f"📍 **Location:** {event['primary_loc']}")
            
            with col2:
                avg_rating, num_ratings = get_event_rating(event['event_id'])
                if avg_rating:
                    st.markdown(f"⭐ **Rating:** {avg_rating}/5 ({num_ratings} reviews)")

# === Analytics Dashboard ===
if st.checkbox("📊 Show Analytics Dashboard"):
    st.subheader("📊 Volunteer Opportunities Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Theme distribution
        if 'Topical Theme' in events_df.columns:
            theme_counts = events_df['Topical Theme'].value_counts()
            fig_pie = px.pie(
                values=theme_counts.values,
                names=theme_counts.index,
                title="Opportunities by Theme"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Location distribution
        if 'primary_loc' in events_df.columns:
            # Extract borough from location
            boroughs = events_df['primary_loc'].str.extract(r'(Manhattan|Brooklyn|Queens|Bronx|Staten Island)', expand=False)
            borough_counts = boroughs.value_counts()
            
            fig_bar = px.bar(
                x=borough_counts.index,
                y=borough_counts.values,
                title="Opportunities by Borough"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# === Footer ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <h4>🌱 NYC Community Event Agent</h4>
    <p>Making it easier to find meaningful volunteer opportunities in New York City</p>
    <p><em>Built with ❤️ for the community</em></p>
</div>
""", unsafe_allow_html=True)
