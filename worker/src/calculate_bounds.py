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
import time

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
            # Use a unique user agent to avoid blocks
            geolocator = Nominatim(user_agent="CityPaper_Worker_Dev_v1", timeout=10)
            
            # Retry logic for rate limits (509)
            location = None
            for attempt in range(3):
                try:
                    # Use the center point to reverse geocode or use the query again
                    location = geolocator.geocode(query, addressdetails=True, language='fr')
                    if location:
                        break
                except Exception as retry_err:
                    logger.warning(f"⚠️ Attempt {attempt+1}/3 failed: {retry_err}")
                    if attempt < 2:
                        sleep_time = 5 * (attempt + 1) # Increased wait time
                        logger.info(f"⏳ Waiting {sleep_time}s before retrying...")
                        time.sleep(sleep_time)

            if location and location.raw and 'address' in location.raw:
                addr = location.raw['address']
                logger.info(f"📋 Raw Address Details: {json.dumps(addr, ensure_ascii=False)}")
                
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
                    "state": addr.get('state') or addr.get('region'), # Map region to state if state is missing, otherwise prefer state
                    "county": addr.get('county'),
                    "postcode": postcode,
                    "city": addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality')
                }
                logger.info(f"📋 Structured Admin Info: {structured_admin}")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch structured address details: {e}")

        # Fallback if structured is empty (e.g. rate limits)
        if not structured_admin and parts:
            logger.info("⚠️ Using fallback parsing from display_name parts")
            # Heuristic: First part is City, Last is Country.
            # Intermediate parts are tricky, but usually [City, County, Region, ..., Country]
            
            fallback_city = parts[0]
            fallback_country = parts[-1]
            fallback_county = parts[1] if len(parts) > 2 else None
            fallback_state = parts[2] if len(parts) > 3 else None
            
            # Try to find postcode in parts
            fallback_postcode = None
            for p in parts:
                if re.match(r'^\d{5}$', p.strip()): # Simple 5-digit check
                     fallback_postcode = p.strip()
                     break
            
            # If no postcode found in parts, try regex on city input or display_name
            if not fallback_postcode:
                 match = re.search(r'\b\d{5}\b', display_name)
                 if match:
                     fallback_postcode = match.group(0)

            structured_admin = {
                "country": fallback_country,
                "state": fallback_state, # Use fallback state (which might be region) as state
                "county": fallback_county,
                "postcode": fallback_postcode,
                "city": fallback_city
            }
            logger.info(f"📋 Fallback Structured Info: {structured_admin}")

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
