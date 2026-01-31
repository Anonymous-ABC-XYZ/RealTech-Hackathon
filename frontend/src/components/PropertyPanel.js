import React from 'react';
import { motion } from 'framer-motion';
import './PropertyPanel.css';

function PropertyPanel({ data, isLoading, onClose }) {
  if (isLoading) {
    return (
      <div className="property-panel">
        <div className="panel-header">
          <div className="skeleton" style={{ width: '60%', height: '24px' }}></div>
          <button className="close-btn" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
        <div className="panel-content">
          <div className="skeleton" style={{ width: '100%', height: '120px', marginBottom: '20px' }}></div>
          <div className="skeleton" style={{ width: '80%', height: '20px', marginBottom: '12px' }}></div>
          <div className="skeleton" style={{ width: '60%', height: '20px', marginBottom: '12px' }}></div>
          <div className="skeleton" style={{ width: '70%', height: '20px' }}></div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-GB').format(value);
  };

  return (
    <motion.div 
      className="property-panel"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="panel-header">
        <h2>Property Analysis</h2>
        <button className="close-btn" onClick={onClose}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>

      <div className="panel-content">
        {/* Price Prediction Card */}
        <div className="prediction-card">
          <div className="prediction-label">Estimated Value</div>
          <div className="prediction-price">
            {formatCurrency(data.prediction.predicted_price)}
          </div>
          <div className="prediction-range">
            <span>{formatCurrency(data.prediction.price_range.low)}</span>
            <div className="range-bar">
              <div 
                className="range-indicator"
                style={{ left: '50%' }}
              ></div>
            </div>
            <span>{formatCurrency(data.prediction.price_range.high)}</span>
          </div>
          <div className="confidence">
            <span>Confidence Score</span>
            <div className="confidence-bar">
              <div 
                className="confidence-fill"
                style={{ width: `${data.prediction.confidence * 100}%` }}
              ></div>
            </div>
            <span>{Math.round(data.prediction.confidence * 100)}%</span>
          </div>
        </div>

        {/* Market Trends */}
        <div className="data-section">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 3V21H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M7 14L12 9L16 13L21 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Market Trends
          </h3>
          <div className="data-grid">
            <div className="data-item">
              <span className="data-value">£{data.area_data.market_trends.avg_price_sqft}</span>
              <span className="data-label">Avg. Price/sqft</span>
            </div>
            <div className="data-item">
              <span className="data-value positive">+{data.area_data.market_trends.yoy_appreciation}%</span>
              <span className="data-label">YoY Growth</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.market_trends.days_on_market}</span>
              <span className="data-label">Days on Market</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.market_trends.inventory_level}</span>
              <span className="data-label">Inventory</span>
            </div>
          </div>
        </div>

        {/* Transport & Accessibility */}
        <div className="data-section">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 6V19M8 6C8 6 8 4 10 4H14C16 4 16 6 16 6M8 6H6C4 6 4 8 4 8V17C4 17 4 19 6 19H8M16 6V19M16 6H18C20 6 20 8 20 8V17C20 17 20 19 18 19H16M16 19H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="7" cy="22" r="1" fill="currentColor"/>
              <circle cx="17" cy="22" r="1" fill="currentColor"/>
            </svg>
            Transport
          </h3>
          <div className="data-grid">
            <div className="data-item">
              <span className="data-value">{data.area_data.transport.nearest_station}</span>
              <span className="data-label">Nearest Station</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.transport.bus_routes}</span>
              <span className="data-label">Bus Routes</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.transport.walk_score}</span>
              <span className="data-label">Walk Score</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.transport.transit_score}</span>
              <span className="data-label">Transit Score</span>
            </div>
          </div>
        </div>

        {/* Demographics */}
        <div className="data-section">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="9" cy="7" r="3" stroke="currentColor" strokeWidth="2"/>
              <path d="M3 21V18C3 15.7909 4.79086 14 7 14H11C13.2091 14 15 15.7909 15 18V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="17" cy="7" r="3" stroke="currentColor" strokeWidth="2"/>
              <path d="M21 21V18C21 16.3431 19.6569 15 18 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Demographics
          </h3>
          <div className="data-grid">
            <div className="data-item">
              <span className="data-value">{formatNumber(data.area_data.demographics.population)}</span>
              <span className="data-label">Population</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.demographics.median_age}</span>
              <span className="data-label">Median Age</span>
            </div>
            <div className="data-item">
              <span className="data-value">£{formatNumber(data.area_data.demographics.median_income)}</span>
              <span className="data-label">Median Income</span>
            </div>
          </div>
        </div>

        {/* Amenities */}
        <div className="data-section">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 21H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M5 21V7L9 4L13 7V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M13 21V11L17 8L21 11V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M9 21V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M17 21V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Nearby Amenities
          </h3>
          <div className="data-grid">
            <div className="data-item">
              <span className="data-value">{data.area_data.amenities.schools_nearby}</span>
              <span className="data-label">Schools</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.amenities.parks_nearby}</span>
              <span className="data-label">Parks</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.amenities.restaurants_nearby}</span>
              <span className="data-label">Restaurants</span>
            </div>
            <div className="data-item">
              <span className="data-value">{data.area_data.amenities.grocery_stores}</span>
              <span className="data-label">Grocery Stores</span>
            </div>
          </div>
        </div>

        {/* Safety */}
        <div className="data-section">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Safety
          </h3>
          <div className="data-grid two-col">
            <div className="data-item">
              <span className="data-value">{data.area_data.safety.crime_index}</span>
              <span className="data-label">Crime Index</span>
            </div>
            <div className="data-item">
              <span className="data-value highlight">{data.area_data.safety.safety_rating}</span>
              <span className="data-label">Safety Rating</span>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="disclaimer">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
            <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            <circle cx="12" cy="16" r="1" fill="currentColor"/>
          </svg>
          <p>This is an AI-generated estimate for demonstration purposes. Actual property values may vary significantly.</p>
        </div>
      </div>
    </motion.div>
  );
}

export default PropertyPanel;
