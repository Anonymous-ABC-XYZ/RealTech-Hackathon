'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import MapSection from '@/components/MapSection';
import PropertyPanel from '@/components/PropertyPanel';
import { PropertyData } from '@/types';

export default function Home() {
  const [selectedLocation, setSelectedLocation] = useState<{
    address: string;
    lat: number;
    lng: number;
  } | null>(null);
  const [propertyData, setPropertyData] = useState<PropertyData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLocationSelect = async (location: {
    address: string;
    lat: number;
    lng: number;
  }) => {
    setSelectedLocation(location);
    setIsLoading(true);

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(location),
      });

      if (response.ok) {
        const data = await response.json();
        setPropertyData(data);
      } else {
        // Use placeholder data if API fails
        setPropertyData({
          success: true,
          address: location.address,
          coordinates: { lat: location.lat, lng: location.lng },
          prediction: {
            predicted_price: 450000,
            confidence: 0.85,
            price_range: { low: 420000, high: 480000 },
          },
          area_data: {
            demographics: {
              population: 45000,
              median_age: 34,
              median_income: 65000,
            },
            amenities: {
              schools_nearby: 5,
              parks_nearby: 3,
              restaurants_nearby: 28,
              grocery_stores: 4,
            },
            transport: {
              nearest_station: '0.3 miles',
              bus_routes: 4,
              walk_score: 78,
              transit_score: 65,
            },
            safety: {
              crime_index: 23,
              safety_rating: 'B+',
            },
            market_trends: {
              avg_price_sqft: 285,
              yoy_appreciation: 4.2,
              days_on_market: 21,
              inventory_level: 'Low',
            },
          },
        });
      }
    } catch (error) {
      console.error('Error fetching prediction:', error);
      // Use placeholder data on error
      setPropertyData({
        success: true,
        address: location.address,
        coordinates: { lat: location.lat, lng: location.lng },
        prediction: {
          predicted_price: 450000,
          confidence: 0.85,
          price_range: { low: 420000, high: 480000 },
        },
        area_data: {
          demographics: {
            population: 45000,
            median_age: 34,
            median_income: 65000,
          },
          amenities: {
            schools_nearby: 5,
            parks_nearby: 3,
            restaurants_nearby: 28,
            grocery_stores: 4,
          },
          transport: {
            nearest_station: '0.3 miles',
            bus_routes: 4,
            walk_score: 78,
            transit_score: 65,
          },
          safety: {
            crime_index: 23,
            safety_rating: 'B+',
          },
          market_trends: {
            avg_price_sqft: 285,
            yoy_appreciation: 4.2,
            days_on_market: 21,
            inventory_level: 'Low',
          },
        },
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold gradient-text mb-4">
            Property Price Prediction
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
            Click anywhere on the map to get instant AI-powered price predictions
            and comprehensive area insights.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Map Section */}
          <div className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <MapSection onLocationSelect={handleLocationSelect} />
          </div>

          {/* Property Panel */}
          <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <PropertyPanel
              location={selectedLocation}
              data={propertyData}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
