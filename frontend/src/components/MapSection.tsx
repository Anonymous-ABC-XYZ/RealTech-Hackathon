'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { MapPin, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

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
      
      const token = process.env.NEXT_PUBLIC_MAPKIT_TOKEN;
      
      if (!mapkit.maps || mapkit.maps.length === 0) {
        mapkit.init({
          authorizationCallback: (done: (token: string) => void) => {
            if (token) {
              done(token);
            } else {
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

    const point = event.pointOnPage;
    const coordinate = map.convertPointOnPageToCoordinate(point);
    
    const lat = coordinate.latitude;
    const lng = coordinate.longitude;

    setSelectedPin({ lat, lng });

    if (annotationRef.current) {
      map.removeAnnotation(annotationRef.current);
    }

    // Modern pin color - using a deep primary color instead of teal
    const annotation = new mapkit.MarkerAnnotation(coordinate, {
      color: '#0f172a', // slate-900 (primary)
      title: 'Selected Location',
      glyphColor: '#ffffff',
    });
    
    annotationRef.current = annotation;
    map.addAnnotation(annotation);

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
        
        mapInstanceRef.current.setCenterAnimated(coordinate);
        
        const lat = coordinate.latitude;
        const lng = coordinate.longitude;
        
        setSelectedPin({ lat, lng });

        if (annotationRef.current) {
          mapInstanceRef.current.removeAnnotation(annotationRef.current);
        }

        const annotation = new mapkit.MarkerAnnotation(coordinate, {
          color: '#0f172a',
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
    <Card className="p-4 h-full min-h-[500px] flex flex-col shadow-sm border-border/60">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-4 flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search address..."
            className="pl-9"
          />
        </div>
        <Button type="submit" variant="secondary">
          Search
        </Button>
      </form>

      {/* Map Container */}
      <div className="flex-1 relative rounded-lg overflow-hidden border border-border bg-muted/20">
        <div ref={mapRef} className="w-full h-full min-h-[400px]" />
        
        {!mapLoaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-muted/10 backdrop-blur-sm">
            <div className="text-center">
              <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin mx-auto mb-3" />
              <p className="text-sm text-muted-foreground font-medium">Loading Map...</p>
            </div>
          </div>
        )}

        {mapLoaded && !selectedPin && (
          <div className="absolute bottom-4 left-4 right-4 flex justify-center pointer-events-none">
            <div className="bg-background/95 backdrop-blur shadow-sm border px-4 py-2 rounded-full flex items-center gap-2 pointer-events-auto">
              <MapPin className="w-3.5 h-3.5 text-primary" />
              <p className="text-xs font-medium">Click to select location</p>
            </div>
          </div>
        )}
      </div>

      {/* Selected location info */}
      {selectedPin && (
        <div className="mt-4 px-3 py-2 bg-muted/40 rounded-md flex items-center gap-2 border border-border/50">
          <MapPin className="w-4 h-4 text-primary" />
          <div className="text-xs">
            <span className="text-muted-foreground">Selected: </span>
            <span className="font-mono font-medium text-foreground">
              {selectedPin.lat.toFixed(5)}, {selectedPin.lng.toFixed(5)}
            </span>
          </div>
        </div>
      )}
    </Card>
  );
}