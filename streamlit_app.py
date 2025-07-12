import streamlit as st
import pandas as pd
import os

# Page config
st.set_page_config(
    page_title="🌱 NYC Volunteer Events",
    page_icon="🌱",
    layout="wide"
)

# Title
st.title("🌱 NYC Community Event Agent")
st.markdown("**Find meaningful volunteer opportunities in New York City**")

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
    
    # Create short description
    merged_df['short_description'] = merged_df['description'].str[:150] + "..."
    
    st.success(f"✅ Merged and loaded {len(merged_df)} volunteer opportunities with REAL locations!")
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
        ]
    }
    
    df = pd.DataFrame(sample_events)
    st.info("📋 Using sample volunteer opportunities for demonstration")
    return df

# Load YOUR REAL DATA
with st.spinner("🔄 Loading your volunteer opportunities..."):
    df = load_volunteer_data()

# Search interface
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "🔍 **What would you like to volunteer for?**",
        placeholder="e.g., help kids, environment, animals, food bank, elderly care..."
    )

with col2:
    search_button = st.button("🚀 **Search**", type="primary", use_container_width=True)

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
        # Search logic
        query_lower = search_query.lower()
        
        # Create search mask
        mask = (
            df['title'].str.lower().str.contains(query_lower, na=False) |
            df['description'].str.lower().str.contains(query_lower, na=False) |
            df.get('Topical Theme', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False) |
            df.get('Mood/Intent', pd.Series(dtype='str')).str.lower().str.contains(query_lower, na=False)
        )
        
        results = df[mask]
        
        if len(results) == 0:
            # Try individual words if no results
            words = query_lower.split()
            for word in words:
                word_mask = (
                    df['title'].str.lower().str.contains(word, na=False) |
                    df['description'].str.lower().str.contains(word, na=False)
                )
                results = pd.concat([results, df[word_mask]]).drop_duplicates()
        
        # Display results
        st.markdown("---")
        if len(results) > 0:
            st.subheader(f"🎯 Found {len(results)} matching opportunities")
            
            # Display each result
            for idx, (_, event) in enumerate(results.head(15).iterrows()):
                with st.container():
                    # Create expandable card for each event
                    with st.expander(f"🌟 {event['title']} - {event['org_title']}", expanded=(idx < 3)):
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**🏢 Organization:** {event['org_title']}")
                            st.markdown(f"**📍 Location:** {event['location_display']}")
                            
                            if 'Topical Theme' in event and event['Topical Theme']:
                                st.markdown(f"**🎯 Theme:** `{event['Topical Theme']}`")
                            
                            if 'Mood/Intent' in event and event['Mood/Intent']:
                                st.markdown(f"**💭 Type:** `{event['Mood/Intent']}`")
                            
                            st.markdown(f"**📝 Description:**")
                            st.markdown(event.get('short_description', event.get('description', '')[:150] + "..."))
                        
                        with col2:
                            st.markdown("**🤝 Get Involved:**")
                            
                            if st.button(f"I'm Interested!", key=f"interest_{idx}"):
                                st.success("🎉 Great! Contact the organization to get started volunteering!")
                            
                            # Simple rating
                            rating = st.selectbox(
                                "Rate this opportunity:",
                                ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
                                key=f"rating_{idx}",
                                index=2
                            )
                            
                            if st.button(f"Submit Rating", key=f"submit_rating_{idx}"):
                                st.success("✅ Thank you for your feedback!")
        else:
            st.info("🔍 No exact matches found. Try different keywords like 'kids', 'environment', 'food', or 'animals'")
    else:
        st.warning("⚠️ Please enter what you'd like to volunteer for!")

else:
    # Default view - show featured opportunities
    st.markdown("---")
    st.subheader("🌟 Featured Volunteer Opportunities")
    st.markdown("*Explore these amazing ways to make a difference in NYC:*")
    
    # Display featured events in a nice grid
    featured_events = df.head(6)
    
    cols = st.columns(2)
    
    for idx, (_, event) in enumerate(featured_events.iterrows()):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                **🌟 {event['title']}**
                
                🏢 **{event['org_title']}**
                
                📍 {event['location_display']}
                
                📝 {event.get('short_description', event.get('description', '')[:120] + "...")}
                """)
                
                if st.button(f"Learn More", key=f"featured_{idx}"):
                    st.info(f"Contact {event['org_title']} to volunteer for {event['title']}!")
                
                st.markdown("---")

# Sidebar with stats and info
with st.sidebar:
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
    <h3>🌱 NYC Community Event Agent</h3>
    <p><em>Connecting volunteers with meaningful opportunities across New York City</em></p>
    <p>💚 <strong>Built with love for the community</strong> 💚</p>
</div>
""", unsafe_allow_html=True)
