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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

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
}: {
  icon: any;
  label: string;
  value: string | number;
  subValue?: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-4 h-4 text-muted-foreground" />
        {subValue && (
          <span className="text-[10px] font-medium bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded-full border border-emerald-100">
            {subValue}
          </span>
        )}
      </div>
      <p className="text-lg font-semibold tracking-tight">{value}</p>
      <p className="text-xs text-muted-foreground font-medium">{label}</p>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="rounded-lg border p-4 space-y-3">
      <Skeleton className="h-4 w-4 rounded-full" />
      <Skeleton className="h-6 w-20" />
      <Skeleton className="h-3 w-16" />
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
      <Card className="h-full min-h-[500px] flex flex-col items-center justify-center text-center p-8 border-dashed shadow-none bg-muted/30">
        <div className="w-16 h-16 rounded-2xl bg-background border flex items-center justify-center mb-4 shadow-sm">
          <MapPin className="w-8 h-8 text-muted-foreground/50" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-1">
          Select Location
        </h3>
        <p className="text-sm text-muted-foreground max-w-xs">
          Choose a point on the map to view detailed analytics and price predictions.
        </p>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className="h-full min-h-[500px] border-none shadow-none bg-transparent">
        <div className="space-y-6">
          <div className="space-y-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-8 w-3/4" />
          </div>
          
          <Skeleton className="h-40 w-full rounded-xl" />
          
          <div className="grid grid-cols-2 gap-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="h-full min-h-[500px] flex flex-col items-center justify-center text-center p-8 border-destructive/20 bg-destructive/5">
        <MapPin className="w-10 h-10 text-destructive/50 mb-4" />
        <h3 className="text-lg font-semibold text-destructive mb-1">
          Data Unavailable
        </h3>
        <p className="text-sm text-muted-foreground">
          Could not fetch property data for this location.
        </p>
      </Card>
    );
  }

  const { prediction, area_data } = data;

  return (
    <div className="space-y-6 h-full overflow-y-auto pr-2 custom-scrollbar">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold tracking-tight text-foreground">
          {location.address}
        </h2>
        <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
          <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
            {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
          </span>
        </div>
      </div>

      {/* Price Prediction Card */}
      <Card className="bg-primary text-primary-foreground border-none overflow-hidden relative">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <TrendingUp className="w-24 h-24" />
        </div>
        <CardContent className="p-6 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <span className="text-primary-foreground/70 text-sm font-medium">
              Estimated Value
            </span>
            <span className="bg-background/20 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-semibold border border-white/10">
              {Math.round(prediction.confidence * 100)}% Confidence
            </span>
          </div>
          <p className="text-4xl font-bold tracking-tighter mb-1">
            {formatCurrency(prediction.predicted_price)}
          </p>
          <p className="text-sm text-primary-foreground/60">
            Range: {formatCurrency(prediction.price_range.low)} -{' '}
            {formatCurrency(prediction.price_range.high)}
          </p>
        </CardContent>
      </Card>

      {/* Demographics Section */}
      <section>
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
          <Users className="w-3.5 h-3.5" />
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
            label="Med. Income"
            value={`£${formatNumber(area_data.demographics.median_income)}`}
          />
        </div>
      </section>

      {/* Amenities Section */}
      <section>
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
          <Building className="w-3.5 h-3.5" />
          Amenities
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
            label="Shops"
            value={area_data.amenities.grocery_stores}
          />
        </div>
      </section>

      {/* Transport Section */}
      <section>
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
          <Train className="w-3.5 h-3.5" />
          Transport
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <DataCard
            icon={Train}
            label="Nearest Stn"
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
      </section>

      {/* Market Trends Section */}
      <section>
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
          <TrendingUp className="w-3.5 h-3.5" />
          Market Trends
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <DataCard
            icon={DollarSign}
            label="Price/sqft"
            value={`£${area_data.market_trends.avg_price_sqft}`}
          />
          <DataCard
            icon={TrendingUp}
            label="Growth (YoY)"
            value={`${area_data.market_trends.yoy_appreciation}%`}
            subValue="Up"
          />
        </div>
      </section>
    </div>
  );
}