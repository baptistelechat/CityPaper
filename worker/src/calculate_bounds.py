import argparse
import json
import sys
import osmnx as ox
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

import re

def calculate_bounds(city, country):
    query = f"{city}, {country}"
    logger.info(f"🔍 Geocoding {query}...")
    
    try:
        # Get the GeoDataFrame
        gdf = ox.geocode_to_gdf(query)
        
        if gdf.empty:
            logger.error(f"❌ No data found for {query}")
            sys.exit(1)
            
        # Get the first result
        row = gdf.iloc[0]
        
        # Bounding Box
        north, south, east, west = row['bbox_north'], row['bbox_south'], row['bbox_east'], row['bbox_west']
        
        # Calculate Center
        center_lat = (north + south) / 2
        center_lon = (east + west) / 2
        
        # Calculate Distance (Radius)
        # Distance from center to a corner (e.g., North-East)
        # We use geodesic distance
        center = (center_lat, center_lon)
        corner = (north, east)
        
        # Calculate diagonal distance from center to corner
        radius_km = geodesic(center, corner).km
        
        # Add padding (5%)
        radius_km_padded = radius_km * 1.05
        
        logger.info(f"📍 Center: {center_lat}, {center_lon}")
        logger.info(f"📏 Radius: {radius_km:.2f} km (Padded: {radius_km_padded:.2f} km)")
        
        # Extract Admin Info for folder structure
        # OSM data varies by country.
        display_name = row.get('display_name', '')
        parts = [p.strip() for p in display_name.split(',')]
        
        # Use Nominatim to get structured address details
        structured_admin = {}
        try:
            geolocator = Nominatim(user_agent="city_paper_worker", timeout=10)
            # Use the center point to reverse geocode or use the query again
            # Using query again is safer to match the user's intent, but using coordinates is safer for the location
            # Let's retry the query with addressdetails
            location = geolocator.geocode(query, addressdetails=True)
            if location and location.raw and 'address' in location.raw:
                addr = location.raw['address']
                
                # Try to find postcode in address, fallback to regex from input city string
                postcode = addr.get('postcode')
                if not postcode:
                    # Regex to find 5 digits in the input city string
                    postcode_match = re.search(r'\b\d{5}\b', city)
                    if postcode_match:
                        postcode = postcode_match.group(0)
                        logger.info(f"🧩 Extracted postcode from input: {postcode}")

                structured_admin = {
                    "country": addr.get('country'),
                    "region": addr.get('region'),
                    "state": addr.get('state'),
                    "county": addr.get('county'),
                    "city": addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality'),
                    "postcode": postcode
                }
                logger.info(f"📋 Structured Admin Info: {structured_admin}")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch structured address details: {e}")

        admin_info = {
            "display_name": display_name,
            "parts": parts,
            "structured": structured_admin
        }
        
        result = {
            "latitude": center_lat,
            "longitude": center_lon,
            "distance": radius_km_padded,
            "admin_info": admin_info
        }
        
        # Print JSON to stdout for the calling script to capture
        print(json.dumps(result))
        
    except Exception as e:
        logger.error(f"❌ Error calculating bounds: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate smart bounds for a city")
    parser.add_argument("--city", required=True, help="City name")
    parser.add_argument("--country", required=True, help="Country name")
    
    args = parser.parse_args()
    
    calculate_bounds(args.city, args.country)
