# Quick Start Guide

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- Google Gemini API key
- Google Maps API key (optional, has fallback)

## Setup (5 minutes)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy this content:
GOOGLE_GENAI_API_KEY=your_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 2. Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Create .env.local file
# Copy this content:
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 3. Install Python Package

```bash
# In backend venv, install wikipedia
pip install wikipedia
```

## Running the Application

### Terminal 1: Backend Server

```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
cd agent
python server.py
```

Server will start on http://localhost:8000

### Terminal 2: Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will start on http://localhost:3000

## First Trip Planning

1. Open browser to http://localhost:3000

2. Allow location access when prompted (to show current location on map)

3. Enter trip details:

   - **Location**: "Paris, France"
   - **Budget**: 3000
   - **Description**: "I want to visit famous landmarks and try French cuisine"

4. Click **"Start Planning"**

5. Wait for search results (you'll see places appear on map with numbers)

6. When prompted, select places:

   - Look at the map and chat for numbered places
   - Enter: "1, 2, 5" (or place names)
   - Click **"Research Selected Places"**

7. Review the research (Wikipedia info, weather, costs)

8. When prompted, choose locations for itinerary:

   - Enter: "1, 2, 3" (the places you want to visit)
   - Click **"Create Itinerary"**

9. Review your complete itinerary!

## Troubleshooting

### Backend won't start

- Check if Python 3.9+ is installed: `python --version`
- Make sure venv is activated (you should see `(venv)` in terminal)
- Check .env file has API keys
- Try: `pip install --upgrade -r requirements.txt`

### Frontend won't start

- Check if Node.js is installed: `node --version`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check .env.local file exists

### Map doesn't show

- Check .env.local has NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
- Restart frontend server after adding .env.local
- Check browser console for errors

### No places found

- If you see "Mock data" message, Google Maps API key is missing
- The app will still work with mock data for testing

### Research fails

- Wikipedia package might not be installed: `pip install wikipedia`
- Some place names might not have Wikipedia pages (this is normal)
- Weather API (wttr.in) might be rate-limited (fallback text will show)

### HITL (Human-in-the-Loop) not working

- Make sure you're entering valid place numbers or names
- Check the chat panel for the list of found places
- Numbers should be comma-separated: "1, 2, 3" not "1 2 3"

## API Keys

### Google Gemini API Key (Required)

1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy to backend/.env as GOOGLE_GENAI_API_KEY

### Google Maps API Key (Optional)

1. Go to https://console.cloud.google.com/
2. Enable Maps JavaScript API and Places API
3. Create API key
4. Copy to both:
   - backend/.env as GOOGLE_MAPS_API_KEY
   - frontend/.env.local as NEXT_PUBLIC_GOOGLE_MAPS_API_KEY

## Features

✅ **Current Location**: Red marker shows your location on map
✅ **Diverse Search**: Finds hotels, attractions, museums, restaurants, heritage sites
✅ **Numbered Markers**: Easy reference (1, 2, 3...)
✅ **Human-in-the-Loop**: You decide which places to research and include
✅ **Rich Research**: Wikipedia history, weather, ratings, tips
✅ **Smart Itinerary**: Day-by-day plan within your budget
✅ **Text-Based Selection**: No clicking required, just type numbers

## Next Steps

- Try different locations (Tokyo, Rome, New York, etc.)
- Experiment with different descriptions
- Review the IMPLEMENTATION_SUMMARY.md for technical details
- Check REQUIREMENTS.md for complete feature list

## Need Help?

- Check console logs in both terminal windows
- Browser developer console (F12) shows frontend errors
- Python errors appear in backend terminal
- Review error\_\*.txt files in backend/ directory if generated
