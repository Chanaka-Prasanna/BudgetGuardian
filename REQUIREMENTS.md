# BudgetGuardian - Project Requirements

## Overview

A travel planning application that uses AI agents to help users discover and plan trips to various locations based on their budget and preferences.

## Frontend Requirements

### Home Screen Layout

- Split-screen interface:
  - **Left Side**: Agent interaction panel for user input and conversation
  - **Right Side**: Map display showing locations
- Map should display user's current location by default

### User Input

Users can enter:

1. **Budget**: Travel budget for the trip
2. **Location**: Destination they want to travel to
3. **Description**: Detailed explanation of their trip preferences

### Display Features

- ❌ Remove budget gauge display
- ❌ Remove place selection on map feature
- ✅ Show locations on map based on search results
- ✅ Interactive agent conversation panel

## Backend Graph Architecture

### High-Level Workflow

#### State 1: Location Search

**Input**: User's budget, destination, and trip description

**Process**:

- Use Google Maps search tool to find relevant places
- Search should return:
  - Hotels
  - Historical heritage sites
  - Towns
  - Cities
  - Tourist attractions
  - Any location matching user preferences

**Output**:

- List of relevant places with details
- If user requests a specific location, return exact match with one item

#### State 2: Human-in-the-Loop - Location Selection

**Input**: List of places from State 1

**Process**:

- Present list of locations to user
- Ask: "Are these locations okay to continue?"
- Allow user to:
  - Remove locations from the list
  - Add additional locations
  - Confirm to proceed

**Output**:

- Finalized list of locations approved by user

#### State 3: Research Phase (Parallel Nodes)

**Input**: Approved list of locations from State 2

**Process**:

- For each location, perform parallel research using free tools
- Gather information:
  - Weather conditions
  - Historical significance
  - Wikipedia information
  - Tourist attractions
  - Local amenities
  - Transportation options
  - Any other relevant details from internet sources

**Output**:

- Structured list of researched items for each location

#### State 4: Human-in-the-Loop - Location Choice

**Input**: Researched information for all locations

**Process**:

- Present detailed research to user
- Ask: "Which locations would you like to choose for your itinerary?"
- User selects preferred locations

**Output**:

- User's selected locations for itinerary planning

#### State 5: Itinerary Planning

**Input**: User's selected locations from State 4

**Process**:

- Create detailed itinerary for chosen locations
- Consider:
  - Budget constraints
  - Travel time between locations
  - Accommodation options
  - Activities and attractions
  - Optimal route planning

**Output**:

- Complete itinerary plan for the trip

## Technical Requirements

### Tools Needed

- Google Maps API/Search tool
- Wikipedia API for historical information
- Weather API for weather data
- Web scraping tools for general internet research
- LLM for content synthesis and planning

### State Management

- Each state should maintain conversation history
- Human-in-the-loop states should wait for user confirmation
- Parallel processing for research phase to improve performance

### Data Structure

Each location should contain:

- Name
- Type (hotel, heritage site, city, etc.)
- Coordinates (lat, lng)
- Research data (weather, history, attractions, etc.)
- Relevance score to user preferences

## User Experience Flow

1. User opens app → sees current location on map
2. User enters budget, destination, and trip description
3. System searches and displays relevant places
4. User reviews and modifies location list (HITL)
5. System researches all approved locations in parallel
6. User reviews research and selects preferred locations (HITL)
7. System generates detailed itinerary
8. User receives complete travel plan

## Features to Remove

- Budget gauge visualization
- Click-to-select places on map
- Any features not aligned with the new workflow

## Features to Implement

- Current location detection and display
- Split-screen interface
- Agent conversation panel
- Human-in-the-loop interaction points
- Parallel research execution
- Structured data presentation
- Itinerary generation
