import argparse
import json
import sys
import osmnx as ox
from geopy.distance import geodesic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

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
        
        # Add padding (10%)
        radius_km_padded = radius_km * 1.1
        
        logger.info(f"📍 Center: {center_lat}, {center_lon}")
        logger.info(f"📏 Radius: {radius_km:.2f} km (Padded: {radius_km_padded:.2f} km)")
        
        # Extract Admin Info for folder structure
        # OSM data varies by country.
        # display_name usually has "City, County/Dept, Region, Country"
        display_name = row.get('display_name', '')
        parts = [p.strip() for p in display_name.split(',')]
        
        # Heuristic for Admin Levels (Fallback)
        # We return the raw parts, the caller can parse them or we do best effort here
        # Usually: City is parts[0], Country is parts[-1]
        # In France: [City, Department, Region, Country]
        
        admin_info = {
            "display_name": display_name,
            "parts": parts
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
