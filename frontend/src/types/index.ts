export interface PropertyData {
  success: boolean;
  address: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  prediction: {
    predicted_price: number;
    confidence: number;
    price_range: {
      low: number;
      high: number;
    };
  };
  area_data: {
    demographics: {
      population: number;
      median_age: number;
      median_income: number;
    };
    amenities: {
      schools_nearby: number;
      parks_nearby: number;
      restaurants_nearby: number;
      grocery_stores: number;
    };
    transport: {
      nearest_station: string;
      bus_routes: number;
      walk_score: number;
      transit_score: number;
    };
    safety: {
      crime_index: number;
      safety_rating: string;
    };
    market_trends: {
      avg_price_sqft: number;
      yoy_appreciation: number;
      days_on_market: number;
      inventory_level: string;
    };
  };
}

export interface LocationData {
  address: string;
  lat: number;
  lng: number;
}
