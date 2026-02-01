'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import MapSection, { SavedLocation } from '@/components/MapSection';
import PropertyPanel from '@/components/PropertyPanel';
import ComparisonChart from '@/components/ComparisonChart';
import { predictResilience } from '@/services/api';

// Helper to extract UK postcode
function extractPostcode(address: string): string | null {
  // Simple regex for UK postcode patterns (e.g., SW7 3RP, EC1A 1BB, W1 2AA)
  const regex = /([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})/;
  const match = address.match(regex);
  return match ? match[0] : null;
}

export default function Home() {
  const [selectedLocation, setSelectedLocation] = useState<{
    address: string;
    lat: number;
    lng: number;
  } | null>(null);
  const [propertyData, setPropertyData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Multi-location comparison state
  const [savedLocations, setSavedLocations] = useState<SavedLocation[]>([]);
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [isCompareMode, setIsCompareMode] = useState(false);

  const handleLocationSelect = async (location: {
    address: string;
    lat: number;
    lng: number;
  }) => {
    setSelectedLocation(location);
    setIsLoading(true);
    setPropertyData(null);
    
    // Exit comparison mode when analyzing a single location
    setIsCompareMode(false);
    setComparisonData([]);

    const postcode = extractPostcode(location.address);

    if (!postcode) {
      console.warn("Could not extract postcode from address:", location.address);
      // Fallback: If no postcode, we can't query the backend efficiently yet.
      // For Hackathon, we could assume a default or ask user.
      // We'll just try querying with the first part of address or fail.
      setIsLoading(false);
      return; 
    }

    try {
      // Call the new Resilience API
      const data = await predictResilience(postcode);
      setPropertyData(data);
    } catch (error) {
      console.error('Error fetching prediction:', error);
      setPropertyData(null); // Or show error state
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
        const postcode = extractPostcode(location.address);
        if (postcode) {
          try {
            return await predictResilience(postcode);
          } catch (e) {
            console.error('Error fetching data for', location.address);
          }
        }
        return null;
      });

      const results = await Promise.all(dataPromises);
      setComparisonData(results.map((r, i) => r || generatePlaceholderData(locations[i])));
    } catch (error) {
      console.error('Error comparing locations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate placeholder resilience data for a location (Fallback)
  const generatePlaceholderData = (location: SavedLocation | { address: string, lat: number, lng: number }): any => ({
    success: true,
    postcode: extractPostcode(location.address) || "UNKNOWN",
    sector: "ESTIMATED",
    current_valuation: {
      value: Math.floor(450000 + Math.random() * 200000),
      currency: "GBP",
    },
    forecasts: {
      '1y': { growth_pct: 2.5, price_value: 461250, risk_penalty_pct: 0.5 },
      '3y': { growth_pct: 8.4, price_value: 487800, risk_penalty_pct: 1.5 },
      '5y': { growth_pct: 15.2, price_value: 518400, risk_penalty_pct: 2.5 },
    },
    resilience: {
      score: 65,
      label: "Medium",
      components: {
        stability: 60,
        growth: 70,
        flood_safety: 85,
        crime_safety: 45,
      },
    },
    risk_factors: {
      flood_risk_level: "Low",
      flood_risk_score: 0,
      historical_volatility: 12.5,
    },
  });

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans antialiased selection:bg-primary/20 selection:text-primary">
      <Header />
      
      <main className="flex-1 flex flex-col container mx-auto px-4 md:px-6 py-8 md:py-12">
        {/* Hero Section - Clean & Minimal */}
        <section className="text-center mb-12 space-y-4 max-w-3xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight lg:text-7xl text-primary">
            PinPoint <span className="text-muted-foreground/50">Property.</span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
            Instant, ML-powered valuation and hyper-local insights for any property.
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
            {isCompareMode ? (
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
                
                {/* Comparison Chart */}
                {!isLoading && comparisonData.length > 0 && (
                  <ComparisonChart 
                    savedLocations={savedLocations} 
                    comparisonData={comparisonData} 
                  />
                )}
                
                {isLoading ? (
                  <div className="space-y-4">
                    {savedLocations.map((_, index) => (
                      <div key={index} className="relative pl-3">
                        <div className="absolute left-0 top-0 bottom-0 w-1 rounded-l bg-muted-foreground/30" />
                        <div className="p-4 bg-muted/50 rounded-lg border animate-pulse">
                          <div className="h-4 bg-muted-foreground/20 rounded w-3/4 mb-3" />
                          <div className="h-3 bg-muted-foreground/20 rounded w-1/2 mb-2" />
                          <div className="h-3 bg-muted-foreground/20 rounded w-2/3" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : comparisonData.length > 0 ? (
                  comparisonData.map((data, index) => (
                    <div key={savedLocations[index]?.id || index} className="relative pl-3">
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
                  ))
                ) : null}
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