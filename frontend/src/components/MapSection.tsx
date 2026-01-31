'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { MapPin, Search } from 'lucide-react';

interface MapSectionProps {
  onLocationSelect: (location: { address: string; lat: number; lng: number }) => void;
}

export default function MapSection({ onLocationSelect }: MapSectionProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedPin, setSelectedPin] = useState<{ lat: number; lng: number } | null>(null);
  const mapInstanceRef = useRef<any>(null);
  const annotationRef = useRef<any>(null);

  // Initialize MapKit
  useEffect(() => {
    const initializeMap = async () => {
      // Check if MapKit is already loaded
      if (typeof window !== 'undefined' && (window as any).mapkit) {
        setupMap();
        return;
      }

      // Load MapKit JS
      const script = document.createElement('script');
      script.src = 'https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js';
      script.crossOrigin = 'anonymous';
      script.async = true;
      
      script.onload = () => {
        setupMap();
      };
      
      document.head.appendChild(script);
    };

    const setupMap = () => {
      const mapkit = (window as any).mapkit;
      
      // Initialize with token (you'll need to get this from Apple Developer)
      const token = process.env.NEXT_PUBLIC_MAPKIT_TOKEN;
      
      if (!mapkit.maps || mapkit.maps.length === 0) {
        mapkit.init({
          authorizationCallback: (done: (token: string) => void) => {
            // For development, we'll use a placeholder. In production, use your JWT token
            if (token) {
              done(token);
            } else {
              // Fallback: Create map without token for demo purposes
              console.warn('MapKit token not found. Map functionality may be limited.');
              done('');
            }
          },
        });
      }

      if (mapRef.current && !mapInstanceRef.current) {
        const map = new mapkit.Map(mapRef.current, {
          center: new mapkit.Coordinate(51.5074, -0.1278), // London default
          mapType: mapkit.Map.MapTypes.Standard,
          showsCompass: mapkit.FeatureVisibility.Hidden,
          showsZoomControl: true,
          showsMapTypeControl: false,
          isRotationEnabled: false,
          colorScheme: mapkit.Map.ColorSchemes.Light,
        });

        mapInstanceRef.current = map;
        setMapLoaded(true);

        // Add click handler
        map.addEventListener('single-tap', handleMapClick);
      }
    };

    initializeMap();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.destroy();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  const handleMapClick = useCallback(async (event: any) => {
    const mapkit = (window as any).mapkit;
    const map = mapInstanceRef.current;
    
    if (!map || !mapkit) return;

    // Convert click point to coordinates
    const point = event.pointOnPage;
    const coordinate = map.convertPointOnPageToCoordinate(point);
    
    const lat = coordinate.latitude;
    const lng = coordinate.longitude;

    setSelectedPin({ lat, lng });

    // Remove existing annotation
    if (annotationRef.current) {
      map.removeAnnotation(annotationRef.current);
    }

    // Add new annotation
    const annotation = new mapkit.MarkerAnnotation(coordinate, {
      color: '#19747E',
      title: 'Selected Location',
      glyphColor: '#ffffff',
    });
    
    annotationRef.current = annotation;
    map.addAnnotation(annotation);

    // Reverse geocode to get address
    const geocoder = new mapkit.Geocoder();
    geocoder.reverseLookup(coordinate, (error: any, data: any) => {
      if (error) {
        console.error('Geocoding error:', error);
        onLocationSelect({
          address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
          lat,
          lng,
        });
        return;
      }

      if (data.results && data.results.length > 0) {
        const place = data.results[0];
        const address = place.formattedAddress || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        
        if (annotationRef.current) {
          annotationRef.current.title = address;
        }
        
        onLocationSelect({ address, lat, lng });
      }
    });
  }, [onLocationSelect]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!searchQuery.trim() || !mapInstanceRef.current) return;

    const mapkit = (window as any).mapkit;
    const geocoder = new mapkit.Geocoder();

    geocoder.lookup(searchQuery, (error: any, data: any) => {
      if (error) {
        console.error('Search error:', error);
        return;
      }

      if (data.results && data.results.length > 0) {
        const place = data.results[0];
        const coordinate = place.coordinate;
        
        // Animate to location
        mapInstanceRef.current.setCenterAnimated(coordinate);
        
        // Simulate a click at this location
        const lat = coordinate.latitude;
        const lng = coordinate.longitude;
        
        setSelectedPin({ lat, lng });

        // Remove existing annotation
        if (annotationRef.current) {
          mapInstanceRef.current.removeAnnotation(annotationRef.current);
        }

        // Add new annotation
        const annotation = new mapkit.MarkerAnnotation(coordinate, {
          color: '#19747E',
          title: place.formattedAddress || searchQuery,
          glyphColor: '#ffffff',
        });
        
        annotationRef.current = annotation;
        mapInstanceRef.current.addAnnotation(annotation);

        onLocationSelect({
          address: place.formattedAddress || searchQuery,
          lat,
          lng,
        });
      }
    });
  };

  return (
    <div className="glass-card rounded-2xl p-6 h-full min-h-[500px] flex flex-col">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for an address..."
            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-dark-cyan focus:ring-2 focus:ring-dark-cyan/20 outline-none transition-all bg-white/80"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 btn-primary px-4 py-1.5 rounded-lg text-white text-sm font-medium"
          >
            Search
          </button>
        </div>
      </form>

      {/* Map Container */}
      <div className="flex-1 relative rounded-xl overflow-hidden map-container bg-platinum">
        <div ref={mapRef} className="w-full h-full min-h-[400px]" />
        
        {/* Loading overlay */}
        {!mapLoaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-platinum">
            <div className="text-center">
              <div className="w-12 h-12 rounded-full border-4 border-dark-cyan border-t-transparent animate-spin mx-auto mb-4" />
              <p className="text-gray-600">Loading map...</p>
            </div>
          </div>
        )}

        {/* Instructions overlay */}
        {mapLoaded && !selectedPin && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-white/90 backdrop-blur-sm rounded-xl px-4 py-3 flex items-center space-x-3 shadow-lg">
              <div className="w-8 h-8 rounded-full bg-dark-cyan/10 flex items-center justify-center">
                <MapPin className="w-4 h-4 text-dark-cyan" />
              </div>
              <p className="text-sm text-gray-600">
                Click anywhere on the map to select a property location
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Selected location info */}
      {selectedPin && (
        <div className="mt-4 p-3 bg-mint/30 rounded-xl flex items-center space-x-3">
          <MapPin className="w-5 h-5 text-dark-cyan" />
          <div className="text-sm">
            <span className="text-gray-600">Selected: </span>
            <span className="font-medium text-gray-800">
              {selectedPin.lat.toFixed(6)}, {selectedPin.lng.toFixed(6)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
