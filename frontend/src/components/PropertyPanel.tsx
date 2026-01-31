'use client';

import { PropertyData } from '@/types';
import {
  TrendingUp,
  Users,
  MapPin,
  Train,
  Shield,
  Building,
  DollarSign,
  Home,
  School,
  Trees,
  UtensilsCrossed,
  ShoppingCart,
  Bus,
  Footprints,
} from 'lucide-react';

interface PropertyPanelProps {
  location: { address: string; lat: number; lng: number } | null;
  data: PropertyData | null;
  isLoading: boolean;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    maximumFractionDigits: 0,
  }).format(value);
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-GB').format(value);
}

function DataCard({
  icon: Icon,
  label,
  value,
  subValue,
  color = 'dark-cyan',
}: {
  icon: any;
  label: string;
  value: string | number;
  subValue?: string;
  color?: string;
}) {
  return (
    <div className="data-card bg-white/60 rounded-xl p-4 border border-gray-100">
      <div className="flex items-start justify-between">
        <div
          className={`w-10 h-10 rounded-lg bg-${color}/10 flex items-center justify-center`}
          style={{ backgroundColor: `rgba(25, 116, 126, 0.1)` }}
        >
          <Icon className="w-5 h-5 text-dark-cyan" />
        </div>
        {subValue && (
          <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
            {subValue}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-800 mt-3">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="bg-white/60 rounded-xl p-4 border border-gray-100">
      <div className="skeleton w-10 h-10 rounded-lg mb-3" />
      <div className="skeleton h-8 w-24 rounded mb-2" />
      <div className="skeleton h-4 w-20 rounded" />
    </div>
  );
}

export default function PropertyPanel({
  location,
  data,
  isLoading,
}: PropertyPanelProps) {
  if (!location) {
    return (
      <div className="glass-card rounded-2xl p-8 h-full min-h-[500px] flex flex-col items-center justify-center text-center">
        <div className="w-20 h-20 rounded-2xl bg-mint/50 flex items-center justify-center mb-6">
          <Home className="w-10 h-10 text-dark-cyan" />
        </div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Select a Location
        </h3>
        <p className="text-gray-500 max-w-sm">
          Click on the map or search for an address to view property price
          predictions and area insights.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="glass-card rounded-2xl p-6 h-full min-h-[500px]">
        <div className="skeleton h-6 w-48 rounded mb-4" />
        <div className="skeleton h-4 w-64 rounded mb-6" />
        
        <div className="skeleton h-32 w-full rounded-xl mb-6" />
        
        <div className="grid grid-cols-2 gap-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-card rounded-2xl p-8 h-full min-h-[500px] flex flex-col items-center justify-center text-center">
        <div className="w-20 h-20 rounded-2xl bg-red-50 flex items-center justify-center mb-6">
          <MapPin className="w-10 h-10 text-red-400" />
        </div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Unable to Load Data
        </h3>
        <p className="text-gray-500 max-w-sm">
          We couldn&apos;t fetch data for this location. Please try again.
        </p>
      </div>
    );
  }

  const { prediction, area_data } = data;

  return (
    <div className="glass-card rounded-2xl p-6 h-full overflow-y-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-2">
          <MapPin className="w-5 h-5 text-dark-cyan" />
          <h2 className="text-lg font-semibold text-gray-800 truncate">
            {location.address}
          </h2>
        </div>
        <p className="text-sm text-gray-500">
          {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
        </p>
      </div>

      {/* Price Prediction Card */}
      <div className="bg-gradient-to-br from-dark-cyan to-emerald-600 rounded-2xl p-6 text-white mb-6">
        <div className="flex items-center justify-between mb-4">
          <span className="text-white/80 text-sm font-medium">
            Predicted Price
          </span>
          <span className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium">
            {Math.round(prediction.confidence * 100)}% confidence
          </span>
        </div>
        <p className="text-4xl font-bold mb-2">
          {formatCurrency(prediction.predicted_price)}
        </p>
        <div className="flex items-center space-x-2 text-white/80 text-sm">
          <TrendingUp className="w-4 h-4" />
          <span>
            Range: {formatCurrency(prediction.price_range.low)} -{' '}
            {formatCurrency(prediction.price_range.high)}
          </span>
        </div>
      </div>

      {/* Demographics Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3 flex items-center">
          <Users className="w-4 h-4 mr-2" />
          Demographics
        </h3>
        <div className="grid grid-cols-3 gap-3">
          <DataCard
            icon={Users}
            label="Population"
            value={formatNumber(area_data.demographics.population)}
          />
          <DataCard
            icon={Users}
            label="Median Age"
            value={area_data.demographics.median_age}
          />
          <DataCard
            icon={DollarSign}
            label="Median Income"
            value={`£${formatNumber(area_data.demographics.median_income)}`}
          />
        </div>
      </div>

      {/* Amenities Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3 flex items-center">
          <Building className="w-4 h-4 mr-2" />
          Nearby Amenities
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <DataCard
            icon={School}
            label="Schools"
            value={area_data.amenities.schools_nearby}
          />
          <DataCard
            icon={Trees}
            label="Parks"
            value={area_data.amenities.parks_nearby}
          />
          <DataCard
            icon={UtensilsCrossed}
            label="Restaurants"
            value={area_data.amenities.restaurants_nearby}
          />
          <DataCard
            icon={ShoppingCart}
            label="Grocery Stores"
            value={area_data.amenities.grocery_stores}
          />
        </div>
      </div>

      {/* Transport Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3 flex items-center">
          <Train className="w-4 h-4 mr-2" />
          Transport
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <DataCard
            icon={Train}
            label="Nearest Station"
            value={area_data.transport.nearest_station}
          />
          <DataCard
            icon={Bus}
            label="Bus Routes"
            value={area_data.transport.bus_routes}
          />
          <DataCard
            icon={Footprints}
            label="Walk Score"
            value={area_data.transport.walk_score}
            subValue="Good"
          />
          <DataCard
            icon={Train}
            label="Transit Score"
            value={area_data.transport.transit_score}
          />
        </div>
      </div>

      {/* Safety Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3 flex items-center">
          <Shield className="w-4 h-4 mr-2" />
          Safety
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <DataCard
            icon={Shield}
            label="Crime Index"
            value={area_data.safety.crime_index}
            subValue="Low"
          />
          <DataCard
            icon={Shield}
            label="Safety Rating"
            value={area_data.safety.safety_rating}
          />
        </div>
      </div>

      {/* Market Trends Section */}
      <div>
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3 flex items-center">
          <TrendingUp className="w-4 h-4 mr-2" />
          Market Trends
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <DataCard
            icon={DollarSign}
            label="Avg Price/sqft"
            value={`£${area_data.market_trends.avg_price_sqft}`}
          />
          <DataCard
            icon={TrendingUp}
            label="YoY Appreciation"
            value={`${area_data.market_trends.yoy_appreciation}%`}
            subValue="Growing"
          />
          <DataCard
            icon={Building}
            label="Days on Market"
            value={area_data.market_trends.days_on_market}
          />
          <DataCard
            icon={Home}
            label="Inventory"
            value={area_data.market_trends.inventory_level}
          />
        </div>
      </div>
    </div>
  );
}
