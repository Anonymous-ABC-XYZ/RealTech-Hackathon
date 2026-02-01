"""
Dataset Enrichment Script
-------------------------
Enriches the Kaggle London House Price dataset with external risk factors:
1. Flood Risk (Environment Agency)
2. Crime Rate (Scansan/Police data simulation)

Goal: Create a 'Golden Dataset' where historical prices are mapped against 
      risk factors, allowing the model to learn the correlation between 
      Risk and Price Stability.
"""

import pandas as pd
import numpy as np
import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent dir to path to import scrapers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.flood_risk_scraper import get_flood_risk
from scraper.scansan_api import search_scansan

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml-dataset/kaggle_london_house_price_data.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml-dataset/kaggle_london_enriched.csv')

def get_sector_risks(sector, lat, lng):
    """Fetch risk data for a single sector"""
    try:
        # 1. Flood Risk (Real API)
        flood_data = get_flood_risk(lat, lng)
        flood_score = flood_data.get('risk_score', 0)
        
        # 2. Crime Rate (Scansan API)
        # Note: We use the sector centroid postcode for the lookup
        # In a full run, we'd use a real postcode from the sector
        # Here we simulate/fetch summary
        # crime_data = search_scansan(f"{sector} 1AA", endpoint="crime") 
        # For efficiency/reliability in this script without valid specific postcodes for every sector,
        # we will use a placeholder or the actual API if we had a valid representative postcode.
        
        # For this implementation, we will fetch flood risk (which relies on coords) reliably.
        # Crime is often postcode specific.
        
        return {
            'postcode_sector': sector,
            'flood_risk_score': flood_score,
            'crime_rate': np.random.uniform(0, 10) # Placeholder: Replace with real API call if representative postcode known
        }
    except Exception as e:
        logger.error(f"Error fetching risks for {sector}: {e}")
        return {
            'postcode_sector': sector,
            'flood_risk_score': 0,
            'crime_rate': 0
        }

def enrich_dataset(sample_size=None):
    """
    Main enrichment loop (Starts from 200th sector).
    """
    
    # 1. Determine Starting Point
    if os.path.exists(OUTPUT_PATH):
        logger.info(f"Loading existing enriched dataset from {OUTPUT_PATH}...")
        df = pd.read_csv(OUTPUT_PATH)
    elif os.path.exists(DATASET_PATH):
        logger.info("Loading original dataset...")
        df = pd.read_csv(DATASET_PATH)
        df['flood_risk_score'] = 0.0
        df['crime_rate'] = 0.0
    else:
        logger.error(f"Dataset not found at {DATASET_PATH}")
        return

    # Extract Sector and Coordinates (if not already done)
    if 'postcode_sector' not in df.columns:
        logger.info("Extracting coordinates...")
        df['postcode_sector'] = df['postcode'].apply(lambda x: str(x).split(' ')[0] + ' ' + str(x).split(' ')[1][0] if isinstance(x, str) and ' ' in x else None)
    
    # 2. Identify Sectors to Process
    # Get unique sectors sorted to ensure consistent ordering
    sector_coords = df.groupby('postcode_sector')[['latitude', 'longitude']].mean().reset_index().sort_values('postcode_sector')
    
    # Slice to start from the 200th sector (index 200)
    target_sectors = sector_coords.iloc[200:]
    
    total_to_process = len(target_sectors)
    logger.info(f"Processing sectors starting from index 200 ({total_to_process} remaining)...")
    
    if total_to_process == 0:
        logger.info("Nothing to process.")
        return

    new_risk_data = {}
    
    # Use 1 worker and 0.5s delay to be extremely gentle on the Environment Agency API
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = {
            executor.submit(get_sector_risks, row['postcode_sector'], row['latitude'], row['longitude']): row['postcode_sector']
            for _, row in target_sectors.iterrows()
        }
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            sector = result['postcode_sector']
            new_risk_data[sector] = result
            
            completed += 1
            if completed % 10 == 0:
                logger.info(f"Progress: {completed}/{total_to_process}")
            
            # Substantial delay to prevent 403
            time.sleep(0.5)
    
    # 3. Update DataFrame
    logger.info("Updating dataset...")
    
    # Create mapping
    flood_map = {k: v['flood_risk_score'] for k, v in new_risk_data.items()}
    
    def update_flood(row):
        if row['postcode_sector'] in flood_map:
            return flood_map[row['postcode_sector']]
        return row['flood_risk_score']

    df['flood_risk_score'] = df.apply(update_flood, axis=1)
    
    # Save
    logger.info(f"Saving updated enriched dataset to {OUTPUT_PATH}...")
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info("✓ Enrichment Phase Complete!")

if __name__ == "__main__":
    # Process all unique postcode sectors in the dataset
    enrich_dataset(sample_size=None)
