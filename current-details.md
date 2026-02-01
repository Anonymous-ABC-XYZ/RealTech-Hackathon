# Scrapers

The data the scrapers fetch:

- Land Registry: Historical sale prices, transaction dates, property type (e.g., Detached), and tenure (Freehold/Leasehold).
- Playwright Rightmove: Current listing price, bedrooms, agent details, key features, and property description.
- Scansan API: Professional valuations, detailed building specs, comprehensive sale history, and local area data.

## ML Models

1. LightGBM (via HistGradientBoostingClassifier): For gradient boosting.
2. Random Forest: For bagging and robustness.
3. Elastic Net (via LogisticRegression with penalty): As a linear baseline.
   - Meta-Learner: A LogisticRegression model is used for stacking these predictions.
   - Uncertainty: Quantile Regressors (LightGBM, Random Forest, ElasticNet) are used to predict confidence intervals (10th, 50th, 90th percentiles).

Columns & Data Used

- Raw Inputs: Price, Date, Property Type, New Build, Tenure, Postcode, District.
- Engineered Features:
  - Temporal: Year, Quarter, Days since 2020.
  - Physical: Flags for is_new_build, is_freehold, is_flat, etc.
  - Market Metrics (Aggregated by Sector): median_price, price_volatility (std dev of returns), price_growth_1yr, max_drawdown.
  - Spatial Lags: Average statistics of neighboring postcode sectors (e.g., spatial_lag_median_price, avg_neighbor_distance_km).
