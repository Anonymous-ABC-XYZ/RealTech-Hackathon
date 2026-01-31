'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import MapSection, { SavedLocation } from '@/components/MapSection';
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
  
  // Multi-location comparison state
  const [savedLocations, setSavedLocations] = useState<SavedLocation[]>([]);
  const [comparisonData, setComparisonData] = useState<PropertyData[]>([]);
  const [isCompareMode, setIsCompareMode] = useState(false);

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

  // Add a location to the comparison list
  const handleAddLocation = (location: SavedLocation) => {
    setSavedLocations(prev => [...prev, location]);
  };

  // Remove a location from the comparison list
  const handleRemoveLocation = (id: string) => {
    setSavedLocations(prev => prev.filter(loc => loc.id !== id));
  };

  // Clear all saved locations
  const handleClearLocations = () => {
    setSavedLocations([]);
    setComparisonData([]);
    setIsCompareMode(false);
  };

  // Compare multiple locations
  const handleCompareLocations = async (locations: SavedLocation[]) => {
    setIsCompareMode(true);
    setIsLoading(true);
    setSelectedLocation(null);
    setPropertyData(null);

    try {
      // Fetch data for all locations
      const dataPromises = locations.map(async (location) => {
        try {
          const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: location.address, lat: location.lat, lng: location.lng }),
          });
          if (response.ok) {
            return await response.json();
          }
        } catch (e) {
          console.error('Error fetching data for', location.address);
        }
        // Return placeholder data
        return generatePlaceholderData(location);
      });

      const results = await Promise.all(dataPromises);
      setComparisonData(results);
    } catch (error) {
      console.error('Error comparing locations:', error);
      // Generate placeholder data for all locations
      setComparisonData(locations.map(loc => generatePlaceholderData(loc)));
    } finally {
      setIsLoading(false);
    }
  };

  // Generate placeholder data for a location
  const generatePlaceholderData = (location: SavedLocation): PropertyData => ({
    success: true,
    address: location.address,
    coordinates: { lat: location.lat, lng: location.lng },
    prediction: {
      predicted_price: Math.floor(350000 + Math.random() * 300000),
      confidence: 0.75 + Math.random() * 0.2,
      price_range: { 
        low: Math.floor(320000 + Math.random() * 200000), 
        high: Math.floor(450000 + Math.random() * 300000) 
      },
    },
    area_data: {
      demographics: {
        population: Math.floor(30000 + Math.random() * 40000),
        median_age: Math.floor(28 + Math.random() * 15),
        median_income: Math.floor(45000 + Math.random() * 40000),
      },
      amenities: {
        schools_nearby: Math.floor(2 + Math.random() * 8),
        parks_nearby: Math.floor(1 + Math.random() * 6),
        restaurants_nearby: Math.floor(10 + Math.random() * 40),
        grocery_stores: Math.floor(2 + Math.random() * 6),
      },
      transport: {
        nearest_station: `${(0.1 + Math.random() * 0.8).toFixed(1)} miles`,
        bus_routes: Math.floor(2 + Math.random() * 8),
        walk_score: Math.floor(50 + Math.random() * 45),
        transit_score: Math.floor(40 + Math.random() * 50),
      },
      safety: {
        crime_index: Math.floor(15 + Math.random() * 30),
        safety_rating: ['A', 'A-', 'B+', 'B', 'B-'][Math.floor(Math.random() * 5)],
      },
      market_trends: {
        avg_price_sqft: Math.floor(200 + Math.random() * 200),
        yoy_appreciation: Number((2 + Math.random() * 6).toFixed(1)),
        days_on_market: Math.floor(14 + Math.random() * 30),
        inventory_level: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
      },
    },
  });

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
            <MapSection 
              onLocationSelect={handleLocationSelect}
              onCompareLocations={handleCompareLocations}
              savedLocations={savedLocations}
              onAddLocation={handleAddLocation}
              onRemoveLocation={handleRemoveLocation}
              onClearLocations={handleClearLocations}
            />
          </div>

          {/* Property Panel - Side panel */}
          <div className="lg:col-span-4 h-full overflow-auto">
            {isCompareMode && comparisonData.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Comparison Results</h3>
                  <button 
                    onClick={() => { setIsCompareMode(false); setComparisonData([]); }}
                    className="text-sm text-muted-foreground hover:text-foreground"
                  >
                    Back to single view
                  </button>
                </div>
                {comparisonData.map((data, index) => (
                  <div key={savedLocations[index]?.id || index} className="relative">
                    <div 
                      className="absolute left-0 top-0 bottom-0 w-1 rounded-l"
                      style={{ backgroundColor: savedLocations[index]?.color || '#0f172a' }}
                    />
                    <PropertyPanel
                      location={savedLocations[index] ? {
                        address: savedLocations[index].address,
                        lat: savedLocations[index].lat,
                        lng: savedLocations[index].lng,
                      } : null}
                      data={data}
                      isLoading={false}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <PropertyPanel
                location={selectedLocation}
                data={propertyData}
                isLoading={isLoading}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}