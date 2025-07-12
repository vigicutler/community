# community# 🌱 NYC Community Event Agent

A smart volunteer opportunity recommender system for New York City.

## Features

- 🔍 **Advanced Search**: Semantic search with synonym expansion
- 🎯 **Smart Recommendations**: Personalized suggestions based on user preferences
- ⭐ **Rating System**: Community-driven event ratings and reviews
- 📊 **Analytics Dashboard**: Visual insights into volunteer opportunities
- 🎨 **Beautiful UI**: Modern, responsive design
- 💾 **Persistent Data**: User preferences and feedback storage

## Setup Instructions

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your CSV file: `Merged_Enriched_Events_CLUSTERED.csv`
4. Run the app: `streamlit run streamlit_app.py`

## Data Format

Your CSV should include these columns:
- `title`: Event title
- `description`: Event description
- `org_title`: Organization name
- `start_date_date`: Event date
- `primary_loc`: Location
- `Topical Theme`: Event category
- `Mood/Intent`: Event type/mood

## Deployment

Deploy to Streamlit Cloud:
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy!
