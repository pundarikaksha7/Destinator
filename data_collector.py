#!/Users/pundarikaksha/Desktop/clones/Destinator/virt/bin/python
import sqlite3
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
import time
import random
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time
from appium.webdriver.common.appiumby import AppiumBy
from uber_scraper import get_uber_fares
from generate_location_pairs import LOCATION_PAIRS
import json 

# Constants
OPENWEATHER_API_KEY = "b9a9b00c3e98ba742521839609c1c501"
GOOGLE_MAPS_API_KEY = "AIzaSyDC2H0UBVTl5TIZoByK-Ps7KItGY58LzEQ"
DB_NAME = "destinator.db"
X = 10  # Number of location pairs per day

# Sample location pairs across Delhi
# LOCATION_PAIRS = [
#     ("Connaught Place", "Saket"),
#     ("Rajouri Garden", "Noida Sector 18"),
#     ("IGI Airport", "Vasant Kunj"),
#     ("Lajpat Nagar", "Karol Bagh"),
#     ("Dwarka Sector 21", "Chandni Chowk"),
#     ("Hauz Khas", "Pitampura"),
#     ("Green Park", "Mayur Vihar"),
#     ("Rohini", "Okhla"),
#     ("South Extension", "Kalkaji"),
#     ("Jor Bagh", "Janakpuri"),
#     ("Khan Market", "New Ashok Nagar"),
#     ("Azadpur", "Nehru Place"),
#     ("Punjabi Bagh", "Badarpur"),
#     ("Ashok Vihar", "Ghitorni"),
# ]

# Initialize geolocator
geolocator = Nominatim(user_agent="destinator")

def get_coordinates(place):
    try:
        location = geolocator.geocode(place + ", Delhi", timeout=10)
        return (location.latitude, location.longitude) if location else None
    except:
        return None

def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return {
            "condition": data["weather"][0]["description"],
            "temp": data["main"]["temp"]
        }
    except:
        return {"condition": "unknown", "temp": None}

def get_distance_and_time(pickup_lat, pickup_lon, drop_lat, drop_lon):
    """
    Fetches driving distance and estimated time with traffic between two coordinates using Google Maps API.

    Returns:
        Tuple of (distance_text, duration_in_traffic_text)
        Returns ("unknown", "unknown") if any error occurs.
    """
    try:
        url = (
            f"https://maps.googleapis.com/maps/api/directions/json?"
            f"origin={pickup_lat},{pickup_lon}"
            f"&destination={drop_lat},{drop_lon}"
            f"&departure_time=now"
            f"&key={GOOGLE_MAPS_API_KEY}"
        )
        response = requests.get(url)
        response.raise_for_status()  # raise error if HTTP request failed
        data = response.json()

        if not data["routes"]:
            print("No routes found.")
            return "unknown", "unknown"

        leg = data["routes"][0]["legs"][0]
        distance = leg["distance"]["text"]
        duration_in_traffic = leg.get("duration_in_traffic", leg["duration"])["text"]

        return distance, duration_in_traffic

    except Exception as e:
        print(f" Error fetching distance/time from Google Maps API: {e}")
        return "unknown", "unknown"



def classify_traffic(pickup_lat, pickup_lon, drop_lat, drop_lon):
    """
    Returns a tuple (traffic_level, classification):
        - traffic_level: Ratio of duration_in_traffic / duration
        - classification: 'no traffic', 'moderate traffic', or 'heavy traffic'
    """
    try:
        url = (
            f"https://maps.googleapis.com/maps/api/directions/json?"
            f"origin={pickup_lat},{pickup_lon}"
            f"&destination={drop_lat},{drop_lon}"
            f"&departure_time=now"
            f"&traffic_model=best_guess"
            f"&key={GOOGLE_MAPS_API_KEY}"
        )

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if (
            not data.get("routes") or
            not data["routes"][0].get("legs") or
            "duration" not in data["routes"][0]["legs"][0]
        ):
            return None, "unknown"

        leg = data["routes"][0]["legs"][0]
        normal_duration_sec = leg["duration"]["value"]
        traffic_duration_sec = leg.get("duration_in_traffic", leg["duration"])["value"]

        if normal_duration_sec == 0:
            return None, "invalid route"

        ratio = traffic_duration_sec / normal_duration_sec

        if ratio <= 1.1:
            return ratio, "no traffic"
        elif ratio <= 1.5:
            return ratio, "moderate traffic"
        else:
            return ratio, "heavy traffic"

    except Exception as e:
        print(f"Error classifying traffic: {e}")
        return None, "unknown"


def insert_into_db(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ride_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pickup_location TEXT,
        drop_location TEXT,
        fare_estimates TEXT,
        travel_distance TEXT,
        travel_time TEXT,
        traffic_level TEXT,
        weather_condition TEXT,
        temperature REAL,
        day_of_week TEXT,
        time_of_day TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''INSERT INTO ride_data (
        pickup_location, drop_location, fare_estimates,
        travel_distance,travel_time,traffic_level, weather_condition, temperature,
        day_of_week, time_of_day
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

def run_daily_job():
    sampled_pairs = random.sample(LOCATION_PAIRS, len(LOCATION_PAIRS))

    for pickup, drop in sampled_pairs:
        coords1 = get_coordinates(pickup)
        coords2 = get_coordinates(drop)
        if not coords1 or not coords2:
            print(f"Skipping pair: {pickup} → {drop} due to location error")
            continue

        now = datetime.now()
        day = now.strftime("%A")
        time_of_day = now.strftime("%H:%M")

        weather = get_weather(*coords1)
        travel_distance,travel_time = get_distance_and_time(*coords1, *coords2)
        traffic_level=classify_traffic(*coords1,*coords2)[1]
        fare_data,err= get_uber_fares(pickup, drop)

        print("Weather: ",weather)
        print("Travel distance: ",travel_distance)
        print("Travel Time: ",travel_time)
        print("Traffic level: ",traffic_level)
        print("Fare Data: ",fare_data)

        if(err): 
            continue


        insert_into_db((
            pickup,
            drop,
            fare_data,
            travel_distance,
            travel_time,
            traffic_level,
            weather["condition"],
            weather["temp"],
            day,
            time_of_day
        ))
        print(f"✅ Collected data for {pickup} → {drop}")
        time.sleep(2)  # Avoid API throttling

# Run once per day (cron or scheduler recommended)
if __name__=="__main__":
    run_daily_job()