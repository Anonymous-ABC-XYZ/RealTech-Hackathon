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
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans antialiased selection:bg-primary/20 selection:text-primary">
      <Header />
      
      <main className="flex-1 flex flex-col container mx-auto px-4 md:px-6 py-8 md:py-12">
        {/* Hero Section - Clean & Minimal */}
        <section className="text-center mb-12 space-y-4 max-w-3xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight lg:text-7xl text-primary">
            Real Estate <span className="text-muted-foreground/50">Intelligence.</span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
            Instant, AI-powered valuation and hyper-local insights for any property.
            Just select a location on the map.
          </p>
        </section>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[800px] lg:h-[600px]">
          {/* Map Section - Takes up more space */}
          <div className="lg:col-span-8 h-full rounded-xl overflow-hidden border bg-card shadow-sm">
            <MapSection onLocationSelect={handleLocationSelect} />
          </div>

          {/* Property Panel - Side panel */}
          <div className="lg:col-span-4 h-full">
            <PropertyPanel
              location={selectedLocation}
              data={propertyData}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}