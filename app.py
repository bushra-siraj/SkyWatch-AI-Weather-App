import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import time
from datetime import datetime
from streamlit_lottie import st_lottie
from plotly import graph_objs as go
# --- CONFIGURATION ---
st.set_page_config(page_title="SkyWatch AI", page_icon="🌤️", layout="wide")

load_dotenv()
API_KEY = os.getenv("API_KEY")

# --- FUNCTIONS ---
def get_current_weather(city):
    """Fetches current weather data."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_forecast(city):
    """Fetches 5-day forecast data."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def load_lottieurl(url: str):
    """Loads a lottie animation from a URL."""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- LOTTIE ANIMATION MAPPING ---
    
def get_lottie_for_condition(condition_code):
    # Mapping based on OpenWeatherMap icon codes
    if condition_code in ['01d']: # Clear Sky Day
        return "https://lottie.host/fbe7a078-f513-489a-b4a6-3faa75300ad3/AtZEG4sQ7S.json"
    
    elif condition_code in ['01n']: # Clear Sky Night
        return "https://lottie.host/592d0859-6a4d-4cc2-851e-d4a56790094d/vjkZJx13qB.json"
    
    elif condition_code in ['02d', '02n', '03d', '03n', '04d', '04n']: # All Cloudy types
        return "https://lottie.host/df927880-a9bb-41bc-806c-cf83dd37d44a/o4WWiYOsJR.json"
    
    elif condition_code in ['09d', '09n', '10d', '10n']: # Rain
        return "https://lottie.host/34ed28ed-6417-4109-b9dc-db107c8748bd/4D7v9r9MBA.json"
    
    else: # Default animation
        return "https://lottie.host/17ff5066-ed15-48da-b12c-bb84cc07c04c/iQibjcEYyR.json"
    
# --- UI COMPONENTS ---
st.title("🌤️ SkyWatch AI Dashboard")
st.markdown("---")

# Sidebar for Input
with st.sidebar:
    st.header("Location")
    city = st.text_input("Enter City Name", "Karachi").title()
    search_button = st.button("Get Dashboard")
    
    st.markdown("---")
    st.subheader("Current Condition")
    # Lottie Placeholder (will be updated dynamically)
    lottie_placeholder = st.empty()

# --- MAIN LOGIC ---
if search_button or city:
    with st.spinner(f"Updating dashboard for {city}..."):
        current_data = get_current_weather(city)
        st.write(f"DEBUG: API Icon Code is {current_data['weather'][0]['icon']}")
        
        if current_data.get("cod") == 200:
            forecast_data = get_forecast(city)
            
            # --- UPDATED LOTTIE ANIMATION LOGIC ---
            # 1. Get the icon code from API (e.g., '10d', '01n')
            icon_code = current_data['weather'][0]['icon']
            
            # 2. Map the icon code to a specific URL
            lottie_url = get_lottie_for_condition(icon_code)
            
            # 3. Load the specific JSON
            lottie_json = load_lottieurl(lottie_url)
            
            # 4. Display the specific animation
            with lottie_placeholder.container():
                if lottie_json:
                    st_lottie(lottie_json, height=150, key=f"anim_{icon_code}") # Added key to force refresh
                else:
                    st.error("Animation failed to load")
            
            # --- DASHBOARD LAYOUT (Widgets) ---
            st.subheader(f"Dashboard: {city}, {current_data['sys']['country']}")
            
            # Row 1: Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Temperature", f"{current_data['main']['temp']}°C", 
                       delta=f"Feels like {current_data['main']['feels_like']}°C")
            col2.metric("Humidity", f"{current_data['main']['humidity']}%")
            
            # Wind Direction Arrow (Dynamic Widget)
            deg = current_data['wind']['deg']
            col3.metric("Wind Speed", f"{current_data['wind']['speed']} m/s")
            col4.markdown(f"**Wind Direction:** {deg}°")
            col4.markdown(f'<div style="transform: rotate({deg}deg); font-size: 30px; margin-top: 10px;">⬆️</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Row 2: Hourly Timeline Graph (Plotly)
            st.subheader("📊 24-Hour Temperature Timeline")
            
            # Prepare Plotly Data
            forecast_list = forecast_data["list"][:8] # Next 24 hours (8 * 3hr)
            times = [datetime.fromtimestamp(item["dt"]).strftime("%H:%M") for item in forecast_list]
            temps = [item["main"]["temp"] for item in forecast_list]
            descriptions = [item["weather"][0]["description"].title() for item in forecast_list]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times, 
                y=temps, 
                mode='lines+markers', 
                name='Temp °C', 
                line=dict(color='#0073e6', width=4),
                marker=dict(size=8),
                hovertemplate="Time: %{x}<br>Temp: %{y}°C<br>Condition: %{text}",
                text=descriptions
            ))
            
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                hovermode="x unified",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="black"),
                xaxis=dict(showgrid=True, gridcolor='lightgray'),
                yaxis=dict(showgrid=True, gridcolor='lightgray')
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("City not found. Please check the spelling.")

st.markdown("---")
st.caption("Powered by OpenWeatherMap API | Built with Streamlit")