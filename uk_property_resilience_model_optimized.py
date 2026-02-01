#!/usr/bin/env python3
"""
UK Property Future Price & Resilience Predictor

Architecture:
- Primary: Multi-Horizon Regression (1yr, 3yr, 5yr Price Forecasts)
- Inputs: Historical Trends + Live Risk Factors (Flood, Crime) + Market Regime
- Logic: ML Forecast + Actuarial Risk Adjustments

"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor
from scipy.spatial import KDTree
import warnings
import os

warnings.filterwarnings('ignore')


class UKPropertyFuturePricePredictor:
    """
    Predicts future property prices and resilience scores.
    """
    
    def __init__(self, n_spatial_neighbors=5, parallel_training=True):
        self.n_spatial_neighbors = n_spatial_neighbors
        self.parallel_training = parallel_training
        
        # Regression Models (One per horizon)
        self.models = {}
        self.horizons = [1, 3, 5] # Years
        
        # Scaler
        self.scaler = StandardScaler()
        
        # Spatial Index
        self.spatial_tree = None
        self.postcode_coords = None
        self.postcode_sectors = None
        
        # Lookup Stats
        self.sector_stats_lookup = {}
        self.default_stats = {}
        self.feature_names = []
        
        # UK Market Regime (Macro-Economic Proxy: Interest Rates/GDP)
        self.MARKET_REGIME = {
            2008: -0.8, 2009: -0.8, # Crash
            2010: -0.2, 2011: -0.2, 2012: -0.1, # Recovery
            2013: 0.3, 2014: 0.4, 2015: 0.4, # Steady
            2016: 0.5, 2017: 0.4, 2018: 0.3, 2019: 0.3, # Growth
            2020: 0.8, 2021: 0.9, # Covid Boom
            2022: 0.2, # Cooling
            2023: -0.6, # Rate Hike Shock
            2024: -0.2, # Stabilization
            2025: 0.1, # Forecast
            2026: 0.3  # Forecast
        }

    # ==================== DATA PREPARATION ====================

    def extract_postcode_sector(self, postcode):
        if pd.isna(postcode) or postcode == '': return None
        postcode = str(postcode).strip().upper()
        parts = postcode.split()
        if len(parts) == 2: return f"{parts[0]} {parts[1][0]}"
        return postcode

    def prepare_time_series_data(self, transactions_df):
        print("\n" + "="*70)
        print("PREPARING TIME-SERIES DATA")
        print("="*70)
        
        df = transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['postcode_sector'] = df['postcode'].apply(self.extract_postcode_sector)
        
        # Aggregate by Sector + Year
        yearly_stats = df.groupby(['postcode_sector', 'year']).agg({
            'price': ['median', 'count', 'std'],
            'flood_risk_score': 'max',
            'crime_rate': 'mean'
        }).reset_index()
        
        yearly_stats.columns = ['postcode_sector', 'year', 'price_median', 'tx_count', 'price_std', 'flood_risk', 'crime_rate']
        yearly_stats = yearly_stats[yearly_stats['tx_count'] >= 3]
        
        processed_data = []
        sectors = yearly_stats['postcode_sector'].unique()
        
        print(f"Processing {len(sectors)} sectors...")
        
        for sector in sectors:
            sector_df = yearly_stats[yearly_stats['postcode_sector'] == sector].sort_values('year')
            sector_df.set_index('year', inplace=True)
            
            years = sector_df.index.values
            
            for current_year in years:
                if current_year < 2000: continue 
                
                # Features: Historical State
                row = {
                    'postcode_sector': sector,
                    'year': current_year,
                    'current_price': sector_df.loc[current_year, 'price_median'],
                    'tx_volume': sector_df.loc[current_year, 'tx_count'],
                    'volatility': sector_df.loc[current_year, 'price_std'] / sector_df.loc[current_year, 'price_median'] if sector_df.loc[current_year, 'price_median'] > 0 else 0,
                    'flood_risk': sector_df.loc[current_year, 'flood_risk'],
                    'crime_rate': sector_df.loc[current_year, 'crime_rate'],
                    'market_regime': self.MARKET_REGIME.get(current_year, 0.0)
                }
                
                # Lag features (Previous years)
                for lag in [1, 3, 5]:
                    prev_year = current_year - lag
                    if prev_year in sector_df.index:
                        row[f'price_lag_{lag}y'] = sector_df.loc[prev_year, 'price_median']
                        row[f'growth_{lag}y'] = (row['current_price'] - row[f'price_lag_{lag}y']) / row[f'price_lag_{lag}y']
                    else:
                        row[f'price_lag_{lag}y'] = row['current_price']
                        row[f'growth_{lag}y'] = 0.0
                
                # Targets: Future Prices
                valid_target = False
                for horizon in self.horizons:
                    target_year = current_year + horizon
                    if target_year in sector_df.index:
                        future_price = sector_df.loc[target_year, 'price_median']
                        row[f'target_growth_{horizon}y'] = (future_price - row['current_price']) / row['current_price']
                        valid_target = True
                    else:
                        row[f'target_growth_{horizon}y'] = None
                
                if valid_target:
                    processed_data.append(row)
                    
        return pd.DataFrame(processed_data)

    # ==================== TRAINING ====================

    def fit(self, transactions_df, postcode_coords_df=None, val_size=0.2):
        if postcode_coords_df is not None:
            self.build_spatial_index(postcode_coords_df)
            
        ts_df = self.prepare_time_series_data(transactions_df)
        
        # Store Latest Stats for Inference
        latest_year = ts_df['year'].max()
        latest_stats = ts_df[ts_df['year'] >= latest_year - 2].sort_values('year', ascending=False)
        self.sector_stats_lookup = latest_stats.groupby('postcode_sector').first().to_dict('index')
        self.default_stats = ts_df.mean(numeric_only=True).to_dict()
        
        # Define Features
        feature_cols = [
            'current_price', 'tx_volume', 'volatility', 
            'flood_risk', 'crime_rate', 'market_regime',
            'growth_1y', 'growth_3y', 'growth_5y'
        ]
        self.feature_names = feature_cols
        X = ts_df[feature_cols]
        
        print("\n" + "="*70)
        print("TRAINING REGRESSORS (RESTORED)")
        print("="*70)
        
        for horizon in self.horizons:
            target_col = f'target_growth_{horizon}y'
            mask = ts_df[target_col].notna()
            X_curr = X[mask]
            y_curr = ts_df.loc[mask, target_col]
            
            X_train, X_val, y_train, y_val = train_test_split(X_curr, y_curr, test_size=val_size, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            if horizon == 1: self.scaler = scaler
            
            model = HistGradientBoostingRegressor(
                max_iter=500, learning_rate=0.05, max_depth=5, 
                l2_regularization=0.5, random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            score = model.score(X_val_scaled, y_val)
            print(f"✓ Horizon +{horizon} Year(s) - R² Score: {score:.4f}")
            self.models[horizon] = model

    def build_spatial_index(self, postcode_coords_df):
        self.postcode_sectors = postcode_coords_df['postcode_sector'].values
        self.postcode_coords = postcode_coords_df[['latitude', 'longitude']].values
        self.spatial_tree = KDTree(self.postcode_coords)

    # ==================== PREDICTION ====================

    def predict(self, current_price, input_features_df):
        """
        Predict future prices with Actuarial Risk Adjustment
        """
        X_scaled = self.scaler.transform(input_features_df[self.feature_names])
        
        results = {
            "current_price": current_price,
            "forecasts": {}
        }
        
        # === ACTUARIAL LOGIC LAYER ===
        # Ensure risks have a guaranteed negative impact on the forecast
        flood_val = input_features_df['flood_risk'].values[0]
        crime_val = input_features_df['crime_rate'].values[0]
        
        # Penalties (Percentage points deducted from growth)
        # Flood Score 0-10: Up to 1.5% penalty per year
        flood_penalty = (flood_val / 10.0) * 0.015 
        
        # Crime Score 0-10: Up to 1.0% penalty per year
        crime_penalty = (crime_val / 10.0) * 0.010
        
        total_annual_penalty = flood_penalty + crime_penalty
        
        for horizon in self.horizons:
            # 1. Get ML Prediction (Base Market Sentiment)
            pred_growth = self.models[horizon].predict(X_scaled)[0]
            
            # 2. Apply Risk Penalty (Compound over horizon)
            # We treat the penalty as an annual drag on growth
            penalty_factor = total_annual_penalty * horizon
            adjusted_growth = pred_growth - penalty_factor
            
            future_price = current_price * (1 + adjusted_growth)
            
            results["forecasts"][f"{horizon}y"] = {
                "growth_pct": round(adjusted_growth * 100, 2),
                "price_value": int(future_price),
                "risk_penalty_pct": round(penalty_factor * 100, 2)
            }
            
        return results

    def get_sector_stats(self, sector):
        return self.sector_stats_lookup.get(sector, self.default_stats)

def load_kaggle_data(filepath):
    try:
        df = pd.read_csv(filepath)
        clean_df = pd.DataFrame()
        if 'history_date' in df.columns:
            clean_df['date'] = pd.to_datetime(df['history_date'], errors='coerce')
            clean_df['price'] = pd.to_numeric(df['history_price'], errors='coerce')
        elif 'date' in df.columns:
            clean_df['date'] = pd.to_datetime(df['date'], errors='coerce')
            clean_df['price'] = pd.to_numeric(df['price'], errors='coerce')
        clean_df['postcode'] = df['postcode']
        clean_df['flood_risk_score'] = df['flood_risk_score'].fillna(0) if 'flood_risk_score' in df.columns else 0
        clean_df['crime_rate'] = df['crime_rate'].fillna(0) if 'crime_rate' in df.columns else 0
        clean_df.dropna(subset=['date', 'price', 'postcode'], inplace=True)
        clean_df = clean_df[clean_df['price'] > 1000]
        return clean_df, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None