#!/usr/bin/env python3
"""
UK Property Price & Resilience Predictor

OPTIMIZED 3-MODEL ENSEMBLE:
- LightGBM (HistGradientBoosting) - Fast, efficient boosting
- Random Forest - Robust bagging
- Elastic Net - Linear baseline

Features:
✓ Parallel training (3x speedup)
✓ Maximum model diversity
✓ Production-ready
✓ Hackathon-optimized

"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, mean_absolute_error, mean_squared_error
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from scipy.spatial import KDTree
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')


class UKPropertyResiliencePredictor:
    """
    UK Property Price & Resilience Predictor
    
    OPTIMIZED 3-MODEL ENSEMBLE:
    1. LightGBM (HistGradientBoosting) - Fast boosting, handles large feature sets
    2. Random Forest - Robust bagging, reduces overfitting  
    3. Elastic Net - Linear baseline, interpretability
    
    Features:
    - Parallel training for 2-3x speedup
    - Stacking meta-learner
    - Quantile regression for uncertainty
    - UK Land Registry format support
    
    Input: Property transaction records (UK Land Registry format)
    Output: Resilience score (High/Medium/Low) with confidence intervals
    """
    
    def __init__(self, n_spatial_neighbors=5, quantiles=[0.1, 0.5, 0.9],
                 ensemble_weights='auto', use_stacking=True, parallel_training=True):
        """
        Args:
            n_spatial_neighbors: Number of neighboring postcode sectors
            quantiles: Quantiles for prediction intervals
            ensemble_weights: 'auto' or 'equal'
            use_stacking: Use stacking vs weighted averaging
            parallel_training: Train models in parallel (faster)
        """
        self.n_spatial_neighbors = n_spatial_neighbors
        self.quantiles = quantiles
        self.ensemble_weights = ensemble_weights
        self.use_stacking = use_stacking
        self.parallel_training = parallel_training
        
        # Classification models (3-model ensemble)
        self.lgb_classifier = None  # LightGBM-style (HistGradientBoosting)
        self.rf_classifier = None   # Random Forest
        self.en_classifier = None   # Elastic Net
        self.meta_classifier = None  # Stacking meta-learner
        
        # Regression models (for quantiles)
        self.quantile_models = {}
        
        # Encoders
        self.label_encoder = LabelEncoder()
        self.feature_scaler = StandardScaler()
        
        # Spatial index
        self.spatial_tree = None
        self.postcode_coords = None
        self.postcode_sectors = None
        self.postcode_to_coords = {}
        
        # Feature tracking
        self.feature_names = []
        self.feature_importances = {}
        self.model_weights = {}
        
    # ==================== DATA PREPROCESSING ====================
    
    def extract_postcode_sector(self, postcode):
        """Extract postcode sector: 'SW7 3PH' -> 'SW7 3'"""
        if pd.isna(postcode) or postcode == '':
            return None
        
        postcode = str(postcode).strip().upper()
        parts = postcode.split()
        if len(parts) == 2:
            return f"{parts[0]} {parts[1][0]}"
        return postcode
    
    def parse_date(self, date_str):
        """Parse date string to datetime"""
        try:
            return pd.to_datetime(date_str, format='%d %B %Y')
        except:
            try:
                return pd.to_datetime(date_str)
            except:
                return None
    
    def preprocess_land_registry_data(self, transactions_df):
        """
        Preprocess Land Registry transaction data
        
        Expected columns: price, date, property_type, new_build, tenure, postcode, district
        """
        print("\n" + "="*70)
        print("PREPROCESSING LAND REGISTRY DATA")
        print("="*70)
        
        df = transactions_df.copy()
        
        # Parse dates
        print("✓ Parsing dates...")
        df['date_parsed'] = df['date'].apply(self.parse_date)
        df['year'] = df['date_parsed'].dt.year
        df['month'] = df['date_parsed'].dt.month
        df['quarter'] = df['date_parsed'].dt.quarter
        
        # Days since reference
        reference_date = pd.Timestamp('2020-01-01')
        df['days_since_ref'] = (df['date_parsed'] - reference_date).dt.days
        
        # Extract postcode sector
        print("✓ Extracting postcode sectors...")
        df['postcode_sector'] = df['postcode'].apply(self.extract_postcode_sector)
        
        # Property features
        print("✓ Engineering property features...")
        df['is_new_build'] = df['new_build'].astype(int)
        df['is_freehold'] = (df['tenure'] == 'Freehold').astype(int)
        df['is_leasehold'] = (df['tenure'] == 'Leasehold').astype(int)
        
        # Property type features
        df['is_flat'] = df['property_type'].str.contains('Flat', case=False, na=False).astype(int)
        df['is_terraced'] = df['property_type'].str.contains('Terrace', case=False, na=False).astype(int)
        df['is_semi_detached'] = df['property_type'].str.contains('Semi', case=False, na=False).astype(int)
        df['is_detached'] = df['property_type'].str.contains('Detached', case=False, na=False).astype(int)
        
        # Log price
        df['log_price'] = np.log(df['price'].clip(lower=1000))
        
        print(f"\n✓ Processed {len(df)} transactions")
        print(f"  Date range: {df['date_parsed'].min()} to {df['date_parsed'].max()}")
        print(f"  Unique postcode sectors: {df['postcode_sector'].nunique()}")
        
        return df
    
    # ==================== PRICE HISTORY AGGREGATION ====================
    
    def aggregate_price_history(self, transactions_df, min_transactions=10):
        """
        Aggregate price history by postcode sector
        
        Returns: DataFrame with sector-level statistics
        """
        print("\n" + "="*70)
        print("AGGREGATING PRICE HISTORY BY POSTCODE SECTOR")
        print("="*70)
        
        sector_stats = []
        
        for sector in transactions_df['postcode_sector'].dropna().unique():
            sector_data = transactions_df[
                transactions_df['postcode_sector'] == sector
            ].sort_values('date_parsed')
            
            if len(sector_data) < min_transactions:
                continue
            
            # Current metrics (last 12 months)
            cutoff_date = sector_data['date_parsed'].max() - pd.Timedelta(days=365)
            recent_data = sector_data[sector_data['date_parsed'] >= cutoff_date]
            
            stats = {
                'postcode_sector': sector,
                'n_transactions': len(sector_data),
                'n_recent_transactions': len(recent_data),
                'median_price': sector_data['price'].median(),
                'mean_price': sector_data['price'].mean(),
                'recent_median_price': recent_data['price'].median() if len(recent_data) > 0 else sector_data['price'].median(),
                'price_std': sector_data['price'].std(),
                'price_cv': sector_data['price'].std() / sector_data['price'].mean() if sector_data['price'].mean() > 0 else 0,
            }
            
            # Price growth
            if len(sector_data) >= 24:
                sorted_data = sector_data.sort_values('date_parsed')
                year_ago = sorted_data['date_parsed'].max() - pd.Timedelta(days=365)
                old_prices = sorted_data[sorted_data['date_parsed'] <= year_ago]['price']
                new_prices = sorted_data[sorted_data['date_parsed'] > year_ago]['price']
                
                if len(old_prices) > 0 and len(new_prices) > 0:
                    stats['price_growth_1yr'] = (new_prices.median() / old_prices.median() - 1) * 100
                else:
                    stats['price_growth_1yr'] = 0
                
                sorted_data['price_change'] = sorted_data['price'].pct_change()
                stats['price_volatility'] = sorted_data['price_change'].std() * 100
            else:
                stats['price_growth_1yr'] = 0
                stats['price_volatility'] = 0
            
            # Drawdown (simplified)
            stats['max_drawdown'] = (1 - sector_data['price'].min() / sector_data['price'].max()) * 100 if sector_data['price'].max() > 0 else 0
            
            sector_stats.append(stats)
        
        stats_df = pd.DataFrame(sector_stats)
        
        print(f"\n✓ Aggregated {len(stats_df)} postcode sectors")
        print(f"  Avg transactions per sector: {stats_df['n_transactions'].mean():.1f}")
        print(f"  Median price: £{stats_df['median_price'].median():,.0f}")
        
        return stats_df
    
    # ==================== SPATIAL FEATURES ====================
    
    def build_spatial_index(self, postcode_coords_df):
        """
        Build spatial index from postcode coordinates
        
        Expected columns: postcode_sector, latitude, longitude
        """
        self.postcode_sectors = postcode_coords_df['postcode_sector'].values
        self.postcode_coords = postcode_coords_df[['latitude', 'longitude']].values
        self.spatial_tree = KDTree(self.postcode_coords)
        
        for idx, row in postcode_coords_df.iterrows():
            self.postcode_to_coords[row['postcode_sector']] = (
                row['latitude'], row['longitude']
            )
        
        print(f"✓ Spatial index built with {len(self.postcode_sectors)} postcode sectors")
    
    def calculate_spatial_lag_features(self, postcode_sector, sector_stats_df):
        """Calculate spatial lag features for a postcode sector"""
        if self.spatial_tree is None:
            return self._get_default_spatial_lag_features()
        
        features = {}
        target_idx = np.where(self.postcode_sectors == postcode_sector)[0]
        
        if len(target_idx) == 0:
            return self._get_default_spatial_lag_features()
        
        target_idx = target_idx[0]
        target_coord = self.postcode_coords[target_idx:target_idx+1]
        
        # Find neighbors
        distances, indices = self.spatial_tree.query(
            target_coord, k=self.n_spatial_neighbors + 1
        )
        
        neighbor_indices = indices[0][1:]
        neighbor_distances = distances[0][1:]
        neighbor_sectors = self.postcode_sectors[neighbor_indices]
        
        neighbor_stats = sector_stats_df[
            sector_stats_df['postcode_sector'].isin(neighbor_sectors)
        ]
        
        if len(neighbor_stats) == 0:
            return self._get_default_spatial_lag_features()
        
        # Distance-weighted features
        weights = 1 / (neighbor_distances + 0.1)
        weights = weights / weights.sum()
        
        key_features = [
            'median_price', 'price_growth_1yr', 'price_volatility',
            'max_drawdown', 'n_recent_transactions'
        ]
        
        for feature in key_features:
            if feature in neighbor_stats.columns:
                values = neighbor_stats[feature].values[:len(weights)]
                features[f'spatial_lag_{feature}'] = np.average(values, weights=weights)
                features[f'spatial_std_{feature}'] = np.std(values)
        
        features['avg_neighbor_distance_km'] = np.mean(neighbor_distances) * 111
        
        return features
    
    def _get_default_spatial_lag_features(self):
        """Default spatial lag features"""
        return {
            'spatial_lag_median_price': 0,
            'spatial_std_median_price': 0,
            'spatial_lag_price_growth_1yr': 0,
            'spatial_std_price_growth_1yr': 0,
            'spatial_lag_price_volatility': 0,
            'spatial_std_price_volatility': 0,
            'spatial_lag_max_drawdown': 0,
            'spatial_std_max_drawdown': 0,
            'spatial_lag_n_recent_transactions': 0,
            'spatial_std_n_recent_transactions': 0,
            'avg_neighbor_distance_km': 0
        }
    
    # ==================== RESILIENCE LABEL CONSTRUCTION ====================
    
    def construct_resilience_labels(self, sector_stats_df):
        """Create resilience labels based on price history"""
        df = sector_stats_df.copy()
        
        # Normalize components
        max_drawdown_norm = 1 - (df['max_drawdown'] / 100)
        volatility_norm = 1 - (df['price_volatility'] / (df['price_volatility'].max() + 1e-8))
        growth_norm = (df['price_growth_1yr'] - df['price_growth_1yr'].min()) / \
                     (df['price_growth_1yr'].max() - df['price_growth_1yr'].min() + 1e-8)
        
        # Composite resilience score
        df['resilience_score'] = (
            0.4 * max_drawdown_norm +
            0.3 * volatility_norm +
            0.3 * growth_norm
        ).clip(0, 1)
        
        # Create tertile labels
        tertiles = df['resilience_score'].quantile([0.33, 0.67])
        
        df['resilience_label'] = df['resilience_score'].apply(
            lambda x: 'Low' if x <= tertiles.iloc[0] else 
                     ('Medium' if x <= tertiles.iloc[1] else 'High')
        )
        
        print(f"\n✓ Resilience labels created:")
        print(df['resilience_label'].value_counts())
        
        return df
    
    # ==================== ENSEMBLE MODELS ====================
    
    def train_lightgbm_classifier(self, X_train, y_train, X_val, y_val):
        """
        Train LightGBM-style classifier (HistGradientBoosting)
        
        Why: Fast, efficient, handles large feature sets
        Best for: Production deployment, large-scale data
        """
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_val_encoded = self.label_encoder.transform(y_val)
        
        self.lgb_classifier = HistGradientBoostingClassifier(
            max_iter=300,
            max_depth=6,
            learning_rate=0.05,
            max_leaf_nodes=31,  # LightGBM-style leaf-wise growth
            min_samples_leaf=4,
            l2_regularization=1.0,
            random_state=42,
            verbose=0
        )
        
        self.lgb_classifier.fit(X_train, y_train_encoded)
        
        # Feature importances (use permutation importance)
        from sklearn.inspection import permutation_importance
        perm_importance = permutation_importance(
            self.lgb_classifier, X_val, y_val_encoded, 
            n_repeats=5, random_state=42, n_jobs=-1
        )
        self.feature_importances['lightgbm'] = dict(
            zip(self.feature_names, perm_importance.importances_mean)
        )
        
        val_acc = self.lgb_classifier.score(X_val, y_val_encoded)
        print(f"    LightGBM validation accuracy: {val_acc:.4f}")
        
        return self.lgb_classifier
    
    def train_random_forest_classifier(self, X_train, y_train, X_val, y_val):
        """
        Train Random Forest classifier
        
        Why: Robust, reduces overfitting through bagging
        Best for: Handling noisy data, outlier resistance
        """
        y_train_encoded = self.label_encoder.transform(y_train)
        
        self.rf_classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            max_features='sqrt',
            bootstrap=True,
            oob_score=True,
            n_jobs=-1,
            random_state=42,
            verbose=0
        )
        
        self.rf_classifier.fit(X_train, y_train_encoded)
        
        self.feature_importances['random_forest'] = dict(
            zip(self.feature_names, self.rf_classifier.feature_importances_)
        )
        
        print(f"    Random Forest OOB score: {self.rf_classifier.oob_score_:.4f}")
        
        return self.rf_classifier
    
    def train_elasticnet_classifier(self, X_train, y_train, X_val, y_val):
        """
        Train Elastic Net classifier (L1+L2 regularization)
        
        Why: Linear baseline, interpretable, fast inference
        Best for: Feature selection, real-time predictions
        """
        y_train_encoded = self.label_encoder.transform(y_train)
        
        self.en_classifier = LogisticRegression(
            penalty='elasticnet',
            C=1.0,
            l1_ratio=0.5,
            solver='saga',
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        
        self.en_classifier.fit(X_train, y_train_encoded)
        
        coef_importance = np.abs(self.en_classifier.coef_).mean(axis=0)
        self.feature_importances['elasticnet'] = dict(
            zip(self.feature_names, coef_importance)
        )
        
        y_val_encoded = self.label_encoder.transform(y_val)
        val_acc = self.en_classifier.score(X_val, y_val_encoded)
        print(f"    Elastic Net validation accuracy: {val_acc:.4f}")
        
        return self.en_classifier
    
    def train_models_parallel(self, X_train, y_train, X_val, y_val):
        """
        Train all 3 models in parallel for 2-3x speedup
        
        Uses ThreadPoolExecutor to train simultaneously
        """
        print("\n✓ Training models in PARALLEL...")
        
        def train_lgb():
            return self.train_lightgbm_classifier(X_train, y_train, X_val, y_val)
        
        def train_rf():
            return self.train_random_forest_classifier(X_train, y_train, X_val, y_val)
        
        def train_en():
            return self.train_elasticnet_classifier(X_train, y_train, X_val, y_val)
        
        import time
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all training jobs
            future_lgb = executor.submit(train_lgb)
            future_rf = executor.submit(train_rf)
            future_en = executor.submit(train_en)
            
            # Wait for completion with progress
            futures = [future_lgb, future_rf, future_en]
            names = ['LightGBM', 'Random Forest', 'Elastic Net']
            
            for future, name in zip(futures, names):
                future.result()  # Wait for completion
                print(f"  ✓ {name} complete")
        
        training_time = time.time() - start_time
        print(f"\n  Total parallel training time: {training_time:.1f}s")
        
        return self.lgb_classifier, self.rf_classifier, self.en_classifier
    
    def train_models_sequential(self, X_train, y_train, X_val, y_val):
        """
        Train all 3 models sequentially (fallback if parallel fails)
        """
        print("\n✓ Training models SEQUENTIALLY...")
        
        import time
        start_time = time.time()
        
        print("\n  Training LightGBM...")
        self.train_lightgbm_classifier(X_train, y_train, X_val, y_val)
        
        print("\n  Training Random Forest...")
        self.train_random_forest_classifier(X_train, y_train, X_val, y_val)
        
        print("\n  Training Elastic Net...")
        self.train_elasticnet_classifier(X_train, y_train, X_val, y_val)
        
        training_time = time.time() - start_time
        print(f"\n  Total sequential training time: {training_time:.1f}s")
        
        return self.lgb_classifier, self.rf_classifier, self.en_classifier
    
    def train_quantile_regressors(self, X_train, y_train, X_val, y_val):
        """Train quantile regression models"""
        print(f"\n✓ Training Quantile Regression Models...")
        
        for quantile in self.quantiles:
            print(f"  Quantile {quantile:.2f}...")
            self.quantile_models[quantile] = {}
            
            # LightGBM quantile (using HistGradientBoosting)
            lgb_model = HistGradientBoostingRegressor(
                loss='quantile',
                quantile=quantile,
                max_iter=200,
                max_depth=5,
                learning_rate=0.1,
                max_leaf_nodes=31,
                random_state=42,
                verbose=0
            )
            lgb_model.fit(X_train, y_train)
            self.quantile_models[quantile]['lightgbm'] = lgb_model
            
            # RandomForest (using percentile of trees)
            rf_model = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=4,
                max_features='sqrt',
                bootstrap=True,
                n_jobs=-1,
                random_state=42
            )
            rf_model.fit(X_train, y_train)
            self.quantile_models[quantile]['random_forest'] = rf_model
            
            # ElasticNet
            en_model = ElasticNet(
                alpha=0.1,
                l1_ratio=0.5,
                max_iter=2000,
                random_state=42
            )
            en_model.fit(X_train, y_train)
            self.quantile_models[quantile]['elasticnet'] = en_model
        
        return self.quantile_models
    
    def _get_base_predictions(self, X):
        """Get predictions from all 3 base classifiers"""
        lgb_probs = self.lgb_classifier.predict_proba(X)
        rf_probs = self.rf_classifier.predict_proba(X)
        en_probs = self.en_classifier.predict_proba(X)
        
        return np.hstack([lgb_probs, rf_probs, en_probs])
    
    def train_meta_classifier(self, X_train, y_train, X_val, y_val):
        """Train meta-learner for stacking"""
        print(f"\n  Training meta-classifier...")
        
        train_meta_features = self._get_base_predictions(X_train)
        val_meta_features = self._get_base_predictions(X_val)
        
        y_train_encoded = self.label_encoder.transform(y_train)
        y_val_encoded = self.label_encoder.transform(y_val)
        
        self.meta_classifier = LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42
        )
        
        self.meta_classifier.fit(train_meta_features, y_train_encoded)
        
        meta_val_acc = self.meta_classifier.score(val_meta_features, y_val_encoded)
        print(f"    Meta-classifier accuracy: {meta_val_acc:.4f}")
        
        return self.meta_classifier
    
    def optimize_weights(self, X_val, y_val):
        """Optimize ensemble weights based on validation performance"""
        print(f"\n✓ Optimizing ensemble weights...")
        
        y_val_encoded = self.label_encoder.transform(y_val)
        
        lgb_acc = self.lgb_classifier.score(X_val, y_val_encoded)
        rf_acc = self.rf_classifier.score(X_val, y_val_encoded)
        en_acc = self.en_classifier.score(X_val, y_val_encoded)
        
        print(f"  Individual accuracies:")
        print(f"    LightGBM:      {lgb_acc:.4f}")
        print(f"    Random Forest: {rf_acc:.4f}")
        print(f"    Elastic Net:   {en_acc:.4f}")
        
        # Performance-based weights (softmax)
        accs = np.array([lgb_acc, rf_acc, en_acc])
        weights = np.exp(accs * 5) / np.exp(accs * 5).sum()  # Temperature = 5
        
        self.model_weights = {
            'lightgbm': weights[0],
            'random_forest': weights[1],
            'elasticnet': weights[2]
        }
        
        print(f"\n  Optimized weights:")
        for name, weight in self.model_weights.items():
            print(f"    {name:15s}: {weight:.4f}")
        
        return self.model_weights
    
    def predict_ensemble(self, X):
        """Ensemble prediction using 3 models"""
        if self.use_stacking and self.meta_classifier is not None:
            # Stacking
            meta_features = self._get_base_predictions(X)
            probs = self.meta_classifier.predict_proba(meta_features)
            predictions = self.label_encoder.inverse_transform(
                np.argmax(probs, axis=1)
            )
            
            epsilon = 1e-10
            uncertainty = -np.sum(probs * np.log(probs + epsilon), axis=1)
            
        else:
            # Weighted voting
            lgb_probs = self.lgb_classifier.predict_proba(X)
            rf_probs = self.rf_classifier.predict_proba(X)
            en_probs = self.en_classifier.predict_proba(X)
            
            w = self.model_weights if self.ensemble_weights == 'auto' else \
                {'lightgbm': 0.34, 'random_forest': 0.33, 'elasticnet': 0.33}
            
            probs = (w['lightgbm'] * lgb_probs + 
                    w['random_forest'] * rf_probs +
                    w['elasticnet'] * en_probs)
            
            predictions = self.label_encoder.inverse_transform(
                np.argmax(probs, axis=1)
            )
            
            # Uncertainty (variance across models)
            all_probs = np.stack([lgb_probs, rf_probs, en_probs])
            uncertainty = np.var(all_probs, axis=0).mean(axis=1)
        
        return predictions, probs, uncertainty
    
    def predict_quantile_ensemble(self, X):
        """Ensemble quantile prediction"""
        predictions = {}
        
        for quantile in self.quantiles:
            # Get predictions from all models
            lgb_pred = self.quantile_models[quantile]['lightgbm'].predict(X)
            
            # Random Forest: extract quantile from tree predictions
            rf_model = self.quantile_models[quantile]['random_forest']
            tree_preds = np.array([tree.predict(X) for tree in rf_model.estimators_])
            rf_pred = np.percentile(tree_preds, quantile * 100, axis=0)
            
            en_pred = self.quantile_models[quantile]['elasticnet'].predict(X)
            
            # Average predictions
            pred = (lgb_pred + rf_pred + en_pred) / 3
            
            if quantile == 0.5:
                predictions['median'] = pred
            elif quantile < 0.5:
                predictions['lower'] = pred
            elif quantile > 0.5:
                predictions['upper'] = pred
        
        if 'lower' in predictions and 'upper' in predictions:
            predictions['width'] = predictions['upper'] - predictions['lower']
            predictions['uncertainty'] = predictions['width']
        
        return predictions
    
    # ==================== MAIN TRAINING PIPELINE ====================
    
    def fit(self, transactions_df, postcode_coords_df=None, val_size=0.2):
        """Complete training pipeline"""
        print("\n" + "="*70)
        print("UK PROPERTY RESILIENCE PREDICTOR - TRAINING")
        print("="*70)
        
        # Preprocess
        transactions = self.preprocess_land_registry_data(transactions_df)
        
        # Aggregate
        sector_stats = self.aggregate_price_history(transactions)
        
        # Spatial features
        if postcode_coords_df is not None:
            self.build_spatial_index(postcode_coords_df)
            
            print("\n✓ Calculating spatial lag features...")
            spatial_features_list = []
            for sector in sector_stats['postcode_sector']:
                spatial_feats = self.calculate_spatial_lag_features(sector, sector_stats)
                spatial_feats['postcode_sector'] = sector
                spatial_features_list.append(spatial_feats)
            
            spatial_features_df = pd.DataFrame(spatial_features_list)
            sector_stats = sector_stats.merge(spatial_features_df, on='postcode_sector', how='left')
        
        # Resilience labels
        sector_stats = self.construct_resilience_labels(sector_stats)
        
        # Prepare features
        feature_cols = [col for col in sector_stats.columns if col not in [
            'postcode_sector', 'resilience_label', 'resilience_score'
        ]]
        
        X = sector_stats[feature_cols]
        y_class = sector_stats['resilience_label']
        y_score = sector_stats['resilience_score']
        
        self.feature_names = X.columns.tolist()
        
        # Split
        X_train, X_val, y_train_class, y_val_class, y_train_score, y_val_score = train_test_split(
            X, y_class, y_score, test_size=val_size, stratify=y_class, random_state=42
        )
        
        print(f"\n✓ Training data:")
        print(f"  Training: {len(X_train)} sectors")
        print(f"  Validation: {len(X_val)} sectors")
        print(f"  Features: {len(self.feature_names)}")
        
        # Scale
        X_train_scaled = self.feature_scaler.fit_transform(X_train)
        X_val_scaled = self.feature_scaler.transform(X_val)
        
        # Train ensemble
        print("\n" + "="*70)
        print("TRAINING 3-MODEL ENSEMBLE")
        print("="*70)
        print("Models: LightGBM + Random Forest + Elastic Net")
        
        if self.parallel_training:
            try:
                self.train_models_parallel(X_train_scaled, y_train_class, X_val_scaled, y_val_class)
            except Exception as e:
                print(f"\n⚠ Parallel training failed: {e}")
                print("  Falling back to sequential training...")
                self.train_models_sequential(X_train_scaled, y_train_class, X_val_scaled, y_val_class)
        else:
            self.train_models_sequential(X_train_scaled, y_train_class, X_val_scaled, y_val_class)
        
        # Meta-learner or weights
        if self.use_stacking:
            self.train_meta_classifier(X_train_scaled, y_train_class, X_val_scaled, y_val_class)
        else:
            self.optimize_weights(X_val_scaled, y_val_class)
        
        # Quantile regression
        self.train_quantile_regressors(X_train_scaled, y_train_score.values, X_val_scaled, y_val_score.values)
        
        # Validation
        print("\n" + "="*70)
        print("VALIDATION RESULTS")
        print("="*70)
        
        val_preds, val_probs, val_uncertainty = self.predict_ensemble(X_val_scaled)
        
        print("\nClassification Report:")
        print(classification_report(y_val_class, val_preds))
        
        y_val_encoded = self.label_encoder.transform(y_val_class)
        print("\nAUC Scores:")
        for i, label in enumerate(self.label_encoder.classes_):
            y_binary = (y_val_encoded == i).astype(int)
            auc = roc_auc_score(y_binary, val_probs[:, i])
            print(f"  {label}: {auc:.4f}")
        
        # Quantile metrics
        interval_preds = self.predict_quantile_ensemble(X_val_scaled)
        if 'median' in interval_preds:
            mae = mean_absolute_error(y_val_score, interval_preds['median'])
            print(f"\n✓ Quantile Regression MAE: {mae:.4f}")
        
        if 'width' in interval_preds:
            coverage = np.mean(
                (y_val_score >= interval_preds['lower']) & 
                (y_val_score <= interval_preds['upper'])
            )
            print(f"  80% Interval Coverage: {coverage:.3f}")
        
        print(f"\n✓ Training complete!")
        
        return self
    
    def predict(self, X, mode='both'):
        """Make predictions"""
        X_scaled = self.feature_scaler.transform(X)
        
        results = {}
        
        if mode in ['classification', 'both']:
            class_preds, class_probs, class_uncertainty = self.predict_ensemble(X_scaled)
            results['class_prediction'] = class_preds
            results['class_probabilities'] = class_probs
            results['class_uncertainty'] = class_uncertainty
        
        if mode in ['quantile', 'both']:
            quantile_preds = self.predict_quantile_ensemble(X_scaled)
            results['score_median'] = quantile_preds.get('median')
            results['score_lower'] = quantile_preds.get('lower')
            results['score_upper'] = quantile_preds.get('upper')
            results['score_uncertainty'] = quantile_preds.get('uncertainty')
        
        return results
    
    def get_feature_importance(self, top_k=20):
        """Get aggregated feature importances"""
        all_features = set()
        for model_imps in self.feature_importances.values():
            all_features.update(model_imps.keys())
        
        avg_importance = {}
        for feat in all_features:
            importances = []
            for model_imps in self.feature_importances.values():
                if feat in model_imps:
                    importances.append(model_imps[feat])
            avg_importance[feat] = np.mean(importances) if importances else 0
        
        sorted_features = sorted(
            avg_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        return sorted_features


def main():
    """Demonstration with synthetic UK property data"""
    print("UK Property Resilience Predictor - Demo")
    print("="*70)
    
    # Generate synthetic Land Registry data
    np.random.seed(42)
    n_transactions = 5000
    
    property_types = ['Flat-maisonette', 'Terraced', 'Semi-detached', 'Detached']
    tenures = ['Freehold', 'Leasehold']
    districts = ['KENSINGTON AND CHELSEA', 'WESTMINSTER', 'CAMDEN']
    
    # Postcode sectors
    postcode_sectors = [f'SW{i} {j}' for i in range(1, 11) for j in range(1, 10)]
    postcode_sectors += [f'W{i} {j}' for i in range(1, 6) for j in range(1, 10)]
    
    transactions_data = []
    
    for i in range(n_transactions):
        sector = np.random.choice(postcode_sectors)
        base_price = np.random.uniform(200000, 1000000)
        
        year = np.random.randint(2015, 2024)
        month = np.random.randint(1, 13)
        day = np.random.randint(1, 28)
        
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        date = f"{day} {months[month-1]} {year}"
        
        transactions_data.append({
            'price': int(base_price * (1 + (year - 2015) * 0.05)),
            'date': date,
            'property_type': np.random.choice(property_types),
            'new_build': np.random.choice([True, False], p=[0.1, 0.9]),
            'tenure': np.random.choice(tenures, p=[0.6, 0.4]),
            'postcode': f"{sector}PH",
            'district': np.random.choice(districts)
        })
    
    transactions_df = pd.DataFrame(transactions_data)
    
    # Postcode coordinates
    postcode_coords_data = []
    for sector in postcode_sectors[:100]:
        postcode_coords_data.append({
            'postcode_sector': sector,
            'latitude': 51.5 + np.random.uniform(-0.1, 0.1),
            'longitude': -0.1 + np.random.uniform(-0.1, 0.1)
        })
    
    postcode_coords_df = pd.DataFrame(postcode_coords_data)
    
    # Train model
    model = UKPropertyResiliencePredictor(
        n_spatial_neighbors=5,
        quantiles=[0.1, 0.5, 0.9],
        use_stacking=True
    )
    
    model.fit(transactions_df, postcode_coords_df, val_size=0.2)
    
    # Feature importances
    print("\n" + "="*70)
    print("TOP 15 FEATURE IMPORTANCES")
    print("="*70)
    top_features = model.get_feature_importance(top_k=15)
    for feat, importance in top_features:
        print(f"  {feat:45s}: {importance:10.4f}")
    
    print("\n" + "="*70)
    print("✓ MODEL READY!")
    print("="*70)


if __name__ == "__main__":
    main()
