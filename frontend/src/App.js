import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import MapSection from './components/MapSection';
import PropertyPanel from './components/PropertyPanel';
import './styles/App.css';

function App() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [propertyData, setPropertyData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLocationSelect = async (location) => {
    setSelectedLocation(location);
    setIsLoading(true);

    // Simulate API call - replace with actual backend call
    setTimeout(() => {
      // Placeholder data - will be replaced with actual API response
      setPropertyData({
        address: location.address,
        coordinates: { lat: location.lat, lng: location.lng },
        prediction: {
          predicted_price: 450000,
          confidence: 0.85,
          price_range: { low: 420000, high: 480000 }
        },
        area_data: {
          demographics: {
            population: 45000,
            median_age: 34,
            median_income: 65000
          },
          amenities: {
            schools_nearby: 5,
            parks_nearby: 3,
            restaurants_nearby: 28,
            grocery_stores: 4
          },
          transport: {
            nearest_station: "0.3 miles",
            bus_routes: 4,
            walk_score: 78,
            transit_score: 65
          },
          safety: {
            crime_index: 23,
            safety_rating: "B+"
          },
          market_trends: {
            avg_price_sqft: 285,
            yoy_appreciation: 4.2,
            days_on_market: 21,
            inventory_level: "Low"
          }
        }
      });
      setIsLoading(false);
    }, 1000);
  };

  const handleClearSelection = () => {
    setSelectedLocation(null);
    setPropertyData(null);
  };

  return (
    <div className="app">
      <Header />
      
      <main className="main-content">
        <div className="hero-section">
          <motion.div 
            className="hero-text"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1>Predict Property Prices with <span className="gradient-text">AI Precision</span></h1>
            <p>Click anywhere on the map to get instant property valuations powered by advanced machine learning</p>
          </motion.div>
        </div>

        <div className="content-grid">
          <motion.div 
            className="map-container"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <MapSection 
              onLocationSelect={handleLocationSelect}
              selectedLocation={selectedLocation}
            />
          </motion.div>

          <AnimatePresence mode="wait">
            {(selectedLocation || isLoading) && (
              <motion.div 
                className="panel-container"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ duration: 0.4 }}
              >
                <PropertyPanel 
                  data={propertyData}
                  isLoading={isLoading}
                  onClose={handleClearSelection}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="footer">
        <p>Built for RealTech Hackathon 2026</p>
      </footer>
    </div>
  );
}

export default App;
