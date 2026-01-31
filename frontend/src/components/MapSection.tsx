'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { MapPin, Search, Plus, X, BarChart3, Trash2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export interface SavedLocation {
  id: string;
  address: string;
  lat: number;
  lng: number;
  color: string;
}

interface MapSectionProps {
  onLocationSelect: (location: { address: string; lat: number; lng: number }) => void;
  onCompareLocations?: (locations: SavedLocation[]) => void;
  savedLocations?: SavedLocation[];
  onAddLocation?: (location: SavedLocation) => void;
  onRemoveLocation?: (id: string) => void;
  onClearLocations?: () => void;
}

// More distinct colors for better differentiation
const PIN_COLORS = [
  '#01161E', // Very dark teal-black
  '#598392', // Medium blue-gray (lighter for contrast)
  '#124559', // Dark cyan
  '#AEC3B0', // Sage green (light for contrast)
  '#2E7D8C', // Bright teal (added for contrast)
  '#8BA399', // Sea green
  '#467385', // Medium blue
  '#D4E5D8', // Very light sage (added for contrast)
];

export default function MapSection({ 
  onLocationSelect,
  onCompareLocations,
  savedLocations = [],
  onAddLocation,
  onRemoveLocation,
  onClearLocations,
}: MapSectionProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [mapLoaded, setMapLoaded] = useState(false);
  const [currentSelection, setCurrentSelection] = useState<{ lat: number; lng: number; address?: string } | null>(null);
  const mapRef = useRef<any>(null);
  const currentMarkerRef = useRef<any>(null);
  const savedMarkersRef = useRef<Map<string, any>>(new Map());
  const LRef = useRef<any>(null);
  
  // Search suggestions state
  const [suggestions, setSuggestions] = useState<Array<{ display_name: string; lat: string; lon: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize Leaflet map
  useEffect(() => {
    const initMap = async () => {
      if (typeof window === 'undefined') return;
      
      // Dynamically import Leaflet
      const L = await import('leaflet');
      LRef.current = L.default;
      
      // Import Leaflet CSS
      await import('leaflet/dist/leaflet.css');

      if (mapContainerRef.current && !mapRef.current) {
        // Create map centered on London
        const map = L.default.map(mapContainerRef.current, {
          center: [51.5074, -0.1278],
          zoom: 13,
          zoomControl: true,
        });

        // Add OpenStreetMap tiles
        L.default.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
          maxZoom: 19,
        }).addTo(map);

        // Handle map clicks
        map.on('click', (e: any) => {
          const { lat, lng } = e.latlng;
          handleMapClick(lat, lng);
        });

        mapRef.current = map;
        setMapLoaded(true);
      }
    };

    initMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Create custom marker icon
  const createMarkerIcon = useCallback((color: string) => {
    const L = LRef.current;
    if (!L) return null;
    
    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="
        background-color: ${color};
        width: 24px;
        height: 24px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 24],
    });
  }, []);

  // Handle map click
  const handleMapClick = useCallback(async (lat: number, lng: number) => {
    const L = LRef.current;
    const map = mapRef.current;
    if (!L || !map) return;

    // Remove current marker
    if (currentMarkerRef.current) {
      map.removeLayer(currentMarkerRef.current);
    }

    // Create new marker
    const color = PIN_COLORS[savedLocations.length % PIN_COLORS.length];
    const icon = createMarkerIcon(color);
    const marker = L.marker([lat, lng], { icon }).addTo(map);
    currentMarkerRef.current = marker;

    // Reverse geocode to get address
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`
      );
      const data = await response.json();
      const address = data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
      
      marker.bindPopup(address).openPopup();
      setCurrentSelection({ lat, lng, address });
    } catch (error) {
      const address = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
      marker.bindPopup(address).openPopup();
      setCurrentSelection({ lat, lng, address });
    }
  }, [savedLocations.length, createMarkerIcon]);

  // Fetch search suggestions
  const fetchSuggestions = async (query: string) => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    setIsSearching(true);
    try {
      const searchQuery = query.toLowerCase().includes('london') 
        ? query 
        : `${query}, London, UK`;
      
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=5&addressdetails=1`
      );
      const data = await response.json();
      setSuggestions(data || []);
    } catch (error) {
      console.error('Search suggestions error:', error);
      setSuggestions([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Handle search input change with debounce
  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    setShowSuggestions(true);

    // Debounce the search
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    searchTimeoutRef.current = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);
  };

  // Handle suggestion selection
  const handleSelectSuggestion = (suggestion: { display_name: string; lat: string; lon: string }) => {
    const latitude = parseFloat(suggestion.lat);
    const longitude = parseFloat(suggestion.lon);
    
    setSearchQuery(suggestion.display_name);
    setSuggestions([]);
    setShowSuggestions(false);
    
    if (mapRef.current) {
      mapRef.current.setView([latitude, longitude], 15);
      handleMapClick(latitude, longitude);
    }
  };

  // Handle search form submit
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    if (!searchQuery.trim() || !mapRef.current) return;

    try {
      // Add London bias to search
      const query = searchQuery.toLowerCase().includes('london') 
        ? searchQuery 
        : `${searchQuery}, London, UK`;
      
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
      );
      const data = await response.json();
      
      if (data && data.length > 0) {
        const { lat, lon, display_name } = data[0];
        const latitude = parseFloat(lat);
        const longitude = parseFloat(lon);
        
        mapRef.current.setView([latitude, longitude], 15);
        handleMapClick(latitude, longitude);
      }
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  // Sync saved locations with markers
  useEffect(() => {
    const L = LRef.current;
    const map = mapRef.current;
    if (!L || !map || !mapLoaded) return;

    // Remove markers for deleted locations
    savedMarkersRef.current.forEach((marker, id) => {
      if (!savedLocations.find(loc => loc.id === id)) {
        map.removeLayer(marker);
        savedMarkersRef.current.delete(id);
      }
    });

    // Add markers for new locations
    savedLocations.forEach((location) => {
      if (!savedMarkersRef.current.has(location.id)) {
        const icon = createMarkerIcon(location.color);
        const marker = L.marker([location.lat, location.lng], { icon })
          .addTo(map)
          .bindPopup(location.address);
        savedMarkersRef.current.set(location.id, marker);
      }
    });
  }, [savedLocations, mapLoaded, createMarkerIcon]);

  // Add current selection to saved locations
  const handleAddLocation = () => {
    if (!currentSelection || !onAddLocation) return;
    
    // Check if this location already exists (check by coordinates with small tolerance)
    const isDuplicate = savedLocations.some(loc => 
      Math.abs(loc.lat - currentSelection.lat) < 0.0001 && 
      Math.abs(loc.lng - currentSelection.lng) < 0.0001
    );

    if (isDuplicate) {
      // Don't add duplicate, just clear current selection
      if (currentMarkerRef.current && mapRef.current) {
        mapRef.current.removeLayer(currentMarkerRef.current);
        currentMarkerRef.current = null;
      }
      setCurrentSelection(null);
      setSearchQuery('');
      return;
    }

    const newLocation: SavedLocation = {
      id: `loc-${Date.now()}`,
      address: currentSelection.address || `${currentSelection.lat.toFixed(6)}, ${currentSelection.lng.toFixed(6)}`,
      lat: currentSelection.lat,
      lng: currentSelection.lng,
      color: PIN_COLORS[savedLocations.length % PIN_COLORS.length],
    };

    // Move current marker to saved
    if (currentMarkerRef.current) {
      savedMarkersRef.current.set(newLocation.id, currentMarkerRef.current);
      currentMarkerRef.current = null;
    }

    onAddLocation(newLocation);
    setCurrentSelection(null);
    setSearchQuery('');
  };

  // Analyze single location
  const handleAnalyzeSingle = () => {
    if (!currentSelection) return;
    onLocationSelect({
      address: currentSelection.address || `${currentSelection.lat.toFixed(6)}, ${currentSelection.lng.toFixed(6)}`,
      lat: currentSelection.lat,
      lng: currentSelection.lng,
    });
  };

  // Compare all saved locations
  const handleCompare = () => {
    if (onCompareLocations && savedLocations.length >= 2) {
      onCompareLocations(savedLocations);
    }
  };

  // Select a saved location for viewing/analysis
  const handleSelectSaved = (location: SavedLocation) => {
    const map = mapRef.current;
    if (!map) return;

    // Pan to the location
    map.setView([location.lat, location.lng], 15);
    
    // Open the popup for this marker
    const marker = savedMarkersRef.current.get(location.id);
    if (marker) {
      marker.openPopup();
    }

    // Set as current selection
    setCurrentSelection({
      lat: location.lat,
      lng: location.lng,
      address: location.address,
    });
  };

  // Remove a saved location
  const handleRemove = (id: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the select handler
    const map = mapRef.current;
    if (map && savedMarkersRef.current.has(id)) {
      map.removeLayer(savedMarkersRef.current.get(id));
      savedMarkersRef.current.delete(id);
    }
    onRemoveLocation?.(id);
  };

  // Clear all locations
  const handleClearAll = () => {
    const map = mapRef.current;
    if (map) {
      savedMarkersRef.current.forEach((marker) => {
        map.removeLayer(marker);
      });
      savedMarkersRef.current.clear();
      if (currentMarkerRef.current) {
        map.removeLayer(currentMarkerRef.current);
        currentMarkerRef.current = null;
      }
    }
    setCurrentSelection(null);
    onClearLocations?.();
  };

  return (
    <Card className="p-4 h-full min-h-[500px] flex flex-col shadow-sm border-border/60">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-4 flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground z-10" />
          <Input
            type="text"
            value={searchQuery}
            onChange={handleSearchInputChange}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Search London address..."
            className="pl-9"
          />
          
          {/* Dropdown suggestions */}
          {showSuggestions && (suggestions.length > 0 || isSearching) && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-border rounded-md shadow-lg z-50 max-h-64 overflow-y-auto">
              {isSearching ? (
                <div className="px-3 py-2 text-sm text-muted-foreground flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                  Searching...
                </div>
              ) : (
                suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleSelectSuggestion(suggestion)}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-muted/50 border-b border-border/50 last:border-b-0 flex items-start gap-2 transition-colors"
                  >
                    <MapPin className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                    <span className="line-clamp-2">{suggestion.display_name}</span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>
        <Button type="submit" variant="secondary">
          Search
        </Button>
      </form>

      {/* Map Container */}
      <div className="flex-1 relative rounded-lg overflow-hidden border border-border bg-muted/20">
        <div ref={mapContainerRef} className="w-full h-full min-h-[300px]" style={{ zIndex: 1 }} />
        
        {!mapLoaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-muted/10 backdrop-blur-sm">
            <div className="text-center">
              <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin mx-auto mb-3" />
              <p className="text-sm text-muted-foreground font-medium">Loading Map...</p>
            </div>
          </div>
        )}

        {mapLoaded && !currentSelection && savedLocations.length === 0 && (
          <div className="absolute bottom-4 left-4 right-4 flex justify-center pointer-events-none z-[1000]">
            <div className="bg-background/95 backdrop-blur shadow-sm border px-4 py-2 rounded-full flex items-center gap-2 pointer-events-auto">
              <MapPin className="w-3.5 h-3.5 text-primary" />
              <p className="text-xs font-medium">Click map or search to select location</p>
            </div>
          </div>
        )}
      </div>

      {/* Saved Locations List */}
      {savedLocations.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">
              Saved Locations ({savedLocations.length})
            </span>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleClearAll}
              className="h-6 px-2 text-xs text-destructive hover:text-destructive"
            >
              <Trash2 className="w-3 h-3 mr-1" />
              Clear All
            </Button>
          </div>
          <div className="max-h-28 overflow-y-auto space-y-1">
            {savedLocations.map((location, index) => (
              <div 
                key={location.id}
                onClick={() => handleSelectSaved(location)}
                className="flex items-center gap-2 px-3 py-2 bg-muted/40 rounded-md border border-border/50 group hover:bg-muted/60 cursor-pointer transition-colors"
              >
                <div 
                  className="w-3 h-3 rounded-full shrink-0" 
                  style={{ backgroundColor: location.color }}
                />
                <span className="text-xs font-medium truncate flex-1">
                  {index + 1}. {location.address}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => handleRemove(location.id, e)}
                  className="h-5 w-5 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Current Selection Actions */}
      {currentSelection && (
        <div className="mt-4 space-y-3">
          <div className="px-3 py-2 bg-muted/40 rounded-md flex items-center gap-2 border border-border/50">
            <div 
              className="w-3 h-3 rounded-full shrink-0" 
              style={{ backgroundColor: PIN_COLORS[savedLocations.length % PIN_COLORS.length] }}
            />
            <div className="text-xs flex-1 min-w-0">
              <span className="text-muted-foreground">Current: </span>
              <span className="font-medium text-foreground truncate block">
                {currentSelection.address || `${currentSelection.lat.toFixed(5)}, ${currentSelection.lng.toFixed(5)}`}
              </span>
            </div>
          </div>
          
          <div className="flex gap-2">
            {(() => {
              const isDuplicate = savedLocations.some(loc => 
                Math.abs(loc.lat - currentSelection.lat) < 0.0001 && 
                Math.abs(loc.lng - currentSelection.lng) < 0.0001
              );
              
              return (
                <Button 
                  onClick={handleAddLocation}
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  disabled={savedLocations.length >= 8 || isDuplicate}
                  title={isDuplicate ? "Location already saved" : savedLocations.length >= 8 ? "Maximum 8 locations" : "Add to compare list"}
                >
                  <Plus className="w-4 h-4 mr-1" />
                  {isDuplicate ? "Already Saved" : "Add to Compare"}
                </Button>
              );
            })()}
            <Button 
              onClick={handleAnalyzeSingle}
              size="sm"
              className="flex-1"
            >
              <MapPin className="w-4 h-4 mr-1" />
              Analyze
            </Button>
          </div>
        </div>
      )}

      {/* Compare Button */}
      {savedLocations.length >= 2 && (
        <div className="mt-3">
          <Button 
            onClick={handleCompare}
            className="w-full"
            variant="default"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Compare {savedLocations.length} Locations
          </Button>
        </div>
      )}

      {/* Helper text */}
      {savedLocations.length === 1 && !currentSelection && (
        <p className="mt-3 text-xs text-muted-foreground text-center">
          Add at least one more location to compare
        </p>
      )}
    </Card>
  );
}
