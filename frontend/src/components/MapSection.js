import React, { useState, useEffect, useRef } from 'react';
import './MapSection.css';

function MapSection({ onLocationSelect, selectedLocation }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markerRef = useRef(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);
  const [mapError, setMapError] = useState(null);

  useEffect(() => {
    // Load Apple MapKit JS
    const loadMapKit = async () => {
      if (window.mapkit) {
        initializeMap();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js';
      script.crossOrigin = 'anonymous';
      script.async = true;

      script.onload = () => {
        initializeMap();
      };

      script.onerror = () => {
        setMapError('Failed to load Apple Maps. Using fallback.');
      };

      document.head.appendChild(script);
    };

    const initializeMap = () => {
      if (!window.mapkit || mapInstanceRef.current) return;

      try {
        // Initialize MapKit with a token
        // NOTE: Replace with your actual MapKit JS token from Apple Developer
        window.mapkit.init({
          authorizationCallback: (done) => {
            // For development, you'll need to get a token from Apple Developer
            // This is a placeholder - the map will show a demo mode message
            done('YOUR_MAPKIT_TOKEN_HERE');
          },
        });

        // Create the map
        const map = new window.mapkit.Map(mapRef.current, {
          center: new window.mapkit.Coordinate(51.5074, -0.1278), // London
          zoom: 12,
          showsCompass: window.mapkit.FeatureVisibility.Hidden,
          showsMapTypeControl: false,
          showsZoomControl: true,
        });

        mapInstanceRef.current = map;
        setIsMapLoaded(true);

        // Add click handler
        map.addEventListener('single-tap', (event) => {
          const coordinate = map.convertPointOnPageToCoordinate(event.pointOnPage);
          handleMapClick(coordinate.latitude, coordinate.longitude);
        });
      } catch (error) {
        console.error('MapKit initialization error:', error);
        setMapError('Map initialization failed. Using interactive fallback.');
      }
    };

    loadMapKit();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.destroy();
      }
    };
  }, []);

  const handleMapClick = async (lat, lng) => {
    // Add or update marker
    if (mapInstanceRef.current) {
      if (markerRef.current) {
        mapInstanceRef.current.removeAnnotation(markerRef.current);
      }

      const marker = new window.mapkit.MarkerAnnotation(
        new window.mapkit.Coordinate(lat, lng),
        {
          color: '#19747E',
          title: 'Selected Location',
        }
      );

      markerRef.current = marker;
      mapInstanceRef.current.addAnnotation(marker);
    }

    // Reverse geocode to get address
    const address = await reverseGeocode(lat, lng);

    onLocationSelect({
      lat,
      lng,
      address,
    });
  };

  const reverseGeocode = async (lat, lng) => {
    // Use a geocoding service to get the address
    // For now, return a placeholder
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
      );
      const data = await response.json();
      return data.display_name || `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    } catch (error) {
      return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }
  };

  // Fallback interactive map using a simple click handler
  const handleFallbackClick = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Convert pixel position to approximate coordinates
    // This is a simplified demo - centers around London
    const centerLat = 51.5074;
    const centerLng = -0.1278;
    const latRange = 0.1;
    const lngRange = 0.2;

    const lat = centerLat + (0.5 - y / rect.height) * latRange;
    const lng = centerLng + (x / rect.width - 0.5) * lngRange;

    handleMapClick(lat, lng);
  };

  return (
    <div className="map-section">
      <div className="map-header">
        <div className="map-title">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 21C12 21 5 13.5 5 9C5 5.13401 8.13401 2 12 2C15.866 2 19 5.13401 19 9C19 13.5 12 21 12 21Z" stroke="currentColor" strokeWidth="2"/>
            <circle cx="12" cy="9" r="3" stroke="currentColor" strokeWidth="2"/>
          </svg>
          <span>Select a Location</span>
        </div>
        <div className="map-instructions">
          Click anywhere on the map to select a property
        </div>
      </div>

      <div className="map-wrapper">
        {!mapError ? (
          <div 
            ref={mapRef} 
            className="apple-map"
            style={{ width: '100%', height: '100%' }}
          />
        ) : (
          <div 
            className="fallback-map"
            onClick={handleFallbackClick}
          >
            <div className="fallback-map-content">
              <div className="fallback-grid"></div>
              {selectedLocation && (
                <div 
                  className="fallback-marker"
                  style={{
                    left: `${50 + (selectedLocation.lng + 0.1278) * 500}%`,
                    top: `${50 - (selectedLocation.lat - 51.5074) * 1000}%`,
                  }}
                >
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 21C12 21 5 13.5 5 9C5 5.13401 8.13401 2 12 2C15.866 2 19 5.13401 19 9C19 13.5 12 21 12 21Z" fill="#19747E" stroke="#19747E" strokeWidth="2"/>
                    <circle cx="12" cy="9" r="3" fill="white"/>
                  </svg>
                </div>
              )}
              <div className="fallback-message">
                <p>Interactive Map Demo</p>
                <span>Click anywhere to select a location</span>
              </div>
            </div>
          </div>
        )}

        {!isMapLoaded && !mapError && (
          <div className="map-loading">
            <div className="loading-spinner"></div>
            <span>Loading map...</span>
          </div>
        )}
      </div>

      {selectedLocation && (
        <div className="selected-address">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 21C12 21 5 13.5 5 9C5 5.13401 8.13401 2 12 2C15.866 2 19 5.13401 19 9C19 13.5 12 21 12 21Z" stroke="currentColor" strokeWidth="2"/>
            <circle cx="12" cy="9" r="3" stroke="currentColor" strokeWidth="2"/>
          </svg>
          <span>{selectedLocation.address}</span>
        </div>
      )}
    </div>
  );
}

export default MapSection;
