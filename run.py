import streamlit as st
import json
import os
from serpapi import GoogleSearch
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import base64
from typing import List, Dict, Any
import re
import time
from dateutil.relativedelta import relativedelta

# Initialize the language model with API key from environment
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Gemini client
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

# Initialize SerpAPI tool with API key from environment
serpapi_key = os.getenv("SERPAPI_API_KEY")

# Only initialize search tools if API key is available
if serpapi_key:
    search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="Useful for when you need to answer questions about current events or search the web"
        )
    ]
else:
    # st.warning("⚠️ SERPAPI_API_KEY environment variable is not set. Web search functionality will be limited.")
    tools = []

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Set up Streamlit UI with a travel-friendly theme
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #ff5733;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #555;
    }

    .stSlider > div {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Title and subtitle
st.markdown('<h1 class="title">🧠 AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

# User Inputs Section
st.markdown("### 🧭 Where are you headed?")
source = st.text_input("🛫 Departure City (IATA Code):", "BOM")  # Example: BOM for Mumbai
destination = st.text_input("🛬 Destination (IATA Code):", "DEL")  # Example: DEL for Delhi

st.markdown("### 🗺️ Plan Your Adventure")
num_days = st.slider("🗓️ Trip Duration (days):", 1, 14, 5)

travel_theme = st.selectbox(
    "🎯 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "⛰️ Adventure Trip", "🧳 Solo Exploration"]
)

st.markdown('---')

st.markdown(
    f"""
    <div style="
        text-align: center;
        padding: 15px;
        background-color: #ffecd1;
        border-radius: 10px;
        margin-top: 20px;
    ">
        <h3>✨ Your {travel_theme} to {destination} is about to begin! ✨</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")  # Example: Mar-06, 2025 | 6:20 PM
    except:
        return "N/A"

activity_preferences = st.text_area(
    "🎯 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
    "Relaxing on the beach, exploring historical sites"
)

departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

# Sidebar Setup
st.sidebar.title("🧳 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")

# Travel Preferences
budget = st.sidebar.radio("💸 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("🛫 Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

# Packing Checklist
st.sidebar.subheader("📦 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "👟 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📚 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}

for item, checked in packing_list.items():
    packing_list[item] = st.sidebar.checkbox(item, value=checked)

# Travel Essentials
st.sidebar.subheader("🧾 Travel Essentials")
visa_required = st.sidebar.checkbox("🛂 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")


SERPAPI_KEY = '8367340a59da41e422df03f7aa8a570866bae326fb10f5ca7d3cba8a6001149f'
GOOGLE_API_KEY = 'AIzaSyCHZ-yq2fW-GBAB_kj_nUNOHp92vF5l0MI'
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY


params = {
    'engine': 'google_flights',
    'departure_id': source,
    'arrival_id': destination,
    'outbound_date': str(departure_date),
    'return_date': str(return_date),
    'currency': "INR",
    'hl': 'en',
    'api_key': SERPAPI_KEY
}

def fetch_flights(source, destination, departure_date, return_date):
    params = {
        'engine': 'google_flights',
        'departure_id': source,
        'arrival_id': destination,
        'outbound_date': str(departure_date),
        'return_date': str(return_date),
        'currency': "INR",
        'hl': 'en',
        'api_key': SERPAPI_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results


def extract_cheapest_flights(flight_data):
    best_flights = flight_data.get('best_flights',[])
    sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float('inf')))[:3]
    return sorted_flights


# Create a researcher agent using LangChain with Gemini
researcher_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        'prefix': '''You are a travel researcher. Your tasks are:
        1. Identify the travel destination specified by the user.
        2. Gather detailed information on the destination, including climate, culture and safety tips.
        3. Find popular attractions, landmarks, and must-visit places.
        4. Search for activities that match the user's interests and travel style.
        5. Prioritize information from reliable sources and official travel guides.
        6. Provide well structured summaries with key insights and recommendations.'''
    }
)

# Create a planner agent using LangChain with Gemini
planner_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        'prefix': '''You are a travel planner. Your tasks are:
        1. Gather details about the user's travel preferences and budget.
        2. Create a detailed itinerary with scheduled activities and estimated costs.
        3. Ensure the itinerary includes transportation options and travel time estimates.
        4. Present the itinerary in a clear, structured format.'''
    }
)

# Create a hotel and restaurant finder agent using LangChain with Gemini
hotel_restaurant_finder = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        'prefix': '''You are a hotel and restaurant finder. Your tasks are:
        1. Identify key locations in the user's travel itinerary.
        2. Search for highly rated hotels near those locations.
        3. Search for top-rated restaurants based on cuisine preferences and proximity.
        4. Prioritize results based on user preferences, ratings, and availability.
        5. Provide direct booking links or reservation options where possible.'''
    }
)

# Initialize variables
itinerary = None
hotel_restaurant_results = None
cheapest_flights = None

# Generate Travel Plan
if st.button("🚀 Generate Travel Plan"):
    with st.spinner("✈️ Fetching best flight options..."):
        flight_data = fetch_flights(source, destination, departure_date, return_date)
        cheapest_flights = extract_cheapest_flights(flight_data)

    # AI Processing
    with st.spinner("🧠 Researching best attractions & activities..."):
        research_prompt = (
            f"Research the best attractions and activities in {destination} for a {num_days}-day {travel_theme.lower()} trip. "
            f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. "
            f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}."
        )
        research_results = researcher_agent.run(research_prompt)

    with st.spinner("🍽️ Searching for hotels & restaurants..."):
        hotel_restaurant_prompt = (
            f"Find the best hotels and restaurants near popular attractions in {destination} for a {travel_theme.lower()} trip. "
            f"Budget: {budget}. Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}."
        )
        hotel_restaurant_results = hotel_restaurant_finder.run(hotel_restaurant_prompt)

    with st.spinner("🗺️ Creating your personalized itinerary..."):
        planning_prompt = (
            f"Based on the following data, create a {num_days}-day itinerary for a {travel_theme.lower()} trip to {destination}. "
            f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. "
            f"Hotel Rating: {hotel_rating}. "
            f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. "
            f"Research: {research_results}. "
            f"Flights: {json.dumps(cheapest_flights)}. "
            f"Hotels & Restaurants: {hotel_restaurant_results}."
        )
        itinerary = planner_agent.run(planning_prompt)

# Display Results
if 'cheapest_flights' in locals() and cheapest_flights is not None:
    st.subheader("✈️ Cheapest Flight Options")
    cols = st.columns(len(cheapest_flights))
    for idx, flight in enumerate(cheapest_flights):
        with cols[idx]:
            airline_logo = flight.get("airline_logo", "")
            airline_name = flight.get("airline", "Unknown Airline")
            price = flight.get("price", "Not Available")
            departure = flight.get("departure", {})
            departure_time = format_datetime(departure.get("time", ""))
            departure_airport = departure.get("airport", "")
            
            # Get flight details
            airline_name = flight.get("airline", "Unknown Airline")
            price = flight.get("price", "Price not available")
            total_duration = flight.get("total_duration", "N/A")
            
            # Get flight segments
            flights_info = flight.get("flights", [{}])
            departure = flights_info[0].get("departure_airport", {}) if flights_info else {}
            arrival = flights_info[-1].get("arrival_airport", {}) if flights_info else {}
            
            # Format departure and arrival times
            departure_time = format_datetime(departure.get("time", ""))
            arrival_time = format_datetime(arrival.get("time", ""))
            departure_airport_code = departure.get("iata", "")
            arrival_airport_code = arrival.get("iata", "")
            
            # Generate booking link if available
            booking_token = flight.get("booking_token", "")
            booking_link = f"https://www.google.com/travel/flights?tfs={booking_token}" if booking_token else "#"
            
            # Flight card layout
            try:
                flight_card = f"""
                <div style='
                    border: 1px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    background-color: #ffffff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                        <div>
                            <h4 style='margin: 0 0 5px 0;'>{airline_name}</h4>
                            <p style='margin: 0;'><strong>Price:</strong> <span style='color: #2e7d32; font-size: 1.2em;'>{price}</span></p>
                        </div>
                        {f'<img src="{airline_logo}" width="60" style="border-radius: 5px;" alt="Airline Logo">' if airline_logo else ''}
                    </div>
                    <div style='margin: 10px 0;'>
                        <p style='margin: 5px 0;'><strong>Departure:</strong> {departure_time} from {departure_airport_code}</p>
                        <p style='margin: 5px 0;'><strong>Arrival:</strong> {arrival_time} at {arrival_airport_code}</p>
                        <p style='margin: 5px 0;'><strong>Duration:</strong> {total_duration}</p>
                    </div>
                    <a href='{booking_link}' target='_blank' style='
                        display: block;
                        text-align: center;
                        background-color: #1976d2;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 4px;
                        text-decoration: none;
                        font-weight: 500;
                        margin-top: 10px;
                    '>
                        Book Now
                    </a>
                </div>
                """
                st.markdown(flight_card, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error displaying flight information: {str(e)}")
                st.warning("Could not display flight details. Please try again.")

# Display hotel and restaurant results if available
if 'hotel_restaurant_results' in locals() and hotel_restaurant_results is not None:
    st.subheader("🏨 Hotels & Restaurants 🍽️")
    st.write(hotel_restaurant_results)

# Display itinerary if available
if 'itinerary' in locals() and itinerary is not None:
    st.subheader("🗺️ Your Personalized Itinerary")
    st.write(itinerary)
    st.success("Travel plan generated successfully!")
else:
    st.warning("No flight data available. Please generate a travel plan first.")

# Add a footer
st.markdown("---")
st.markdown("### Need help? Contact our support team at aditya.arya3131@gmail.com")