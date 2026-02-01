'use client';

import {
  TrendingUp,
  TrendingDown,
  Shield,
  Home,
  AlertTriangle,
  Droplets,
  Activity,
  Lock,
  Minus,
  HelpCircle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tooltip } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

// Define the shape of the new API response
interface ResilienceData {
  success: boolean;
  postcode: string;
  sector: string;
  current_valuation: {
    value: number;
    currency: string;
  };
  forecasts: {
    '1y': { growth_pct: number; price_value: number; risk_penalty_pct: number };
    '3y': { growth_pct: number; price_value: number; risk_penalty_pct: number };
    '5y': { growth_pct: number; price_value: number; risk_penalty_pct: number };
  };
  resilience: {
    score: number;
    label: string; // High, Medium, Low
    components: {
      stability: number;
      growth: number;
      flood_safety: number;
      crime_safety: number;
    };
  };
  risk_factors: {
    flood_risk_level: string; // Low, Medium, High
    flood_risk_score: number;
    historical_volatility: number;
  };
}

interface PropertyPanelProps {
  location: { address: string; lat: number; lng: number } | null;
  data: ResilienceData | null;
  isLoading: boolean;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    maximumFractionDigits: 0,
  }).format(value);
}

function getResilienceVariant(label: string): "default" | "secondary" | "destructive" | "outline" {
  switch (label.toLowerCase()) {
    case 'high': return 'default'; // Uses primary color (usually dark/black)
    case 'medium': return 'secondary';
    case 'low': return 'destructive';
    default: return 'outline';
  }
}

function getProgressColor(value: number) {
  if (value >= 75) return 'bg-emerald-500';
  if (value >= 50) return 'bg-amber-500';
  return 'bg-rose-500';
}

function TrendIndicator({ pct }: { pct: number }) {
  if (pct > 0) return <TrendingUp className="w-3 h-3 text-emerald-600" />;
  if (pct < 0) return <TrendingDown className="w-3 h-3 text-rose-600" />;
  return <Minus className="w-3 h-3 text-slate-400" />;
}

export default function PropertyPanel({
  location,
  data,
  isLoading,
}: PropertyPanelProps) {
  if (!location) {
    return (
      <Card className="h-full min-h-[500px] flex flex-col items-center justify-center text-center p-8 border-dashed shadow-sm bg-muted/10">
        <div className="w-16 h-16 rounded-full bg-primary/5 flex items-center justify-center mb-4">
          <Home className="w-8 h-8 text-primary/40" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-1">
          Select Property
        </h3>
        <p className="text-sm text-muted-foreground max-w-xs leading-relaxed">
          Click on the map to generate a comprehensive resilience report and future valuation.
        </p>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className="h-full min-h-[500px] border-none shadow-none bg-transparent p-1">
        <div className="space-y-6">
          <div className="space-y-2">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-1/3" />
          </div>
          <Skeleton className="h-40 w-full rounded-xl" />
          <div className="space-y-4">
            <Skeleton className="h-12 w-full rounded-lg" />
            <Skeleton className="h-12 w-full rounded-lg" />
            <Skeleton className="h-12 w-full rounded-lg" />
          </div>
        </div>
      </Card>
    );
  }

  if (!data || !data.success) {
    return (
      <Card className="h-full min-h-[500px] flex flex-col items-center justify-center text-center p-8 border-destructive/20 bg-destructive/5">
        <AlertTriangle className="w-10 h-10 text-destructive/50 mb-4" />
        <h3 className="text-lg font-semibold text-destructive mb-1">
          Analysis Failed
        </h3>
        <p className="text-sm text-muted-foreground">
          Could not generate resilience report for this location.
        </p>
      </Card>
    );
  }

  const { current_valuation, forecasts, resilience, risk_factors } = data;

  return (
    <div className="space-y-6 h-full overflow-y-auto pr-3 custom-scrollbar">
      {/* Header */}
      <div>
        <h2 className="text-lg font-bold tracking-tight text-foreground leading-snug">
          {location.address}
        </h2>
        <div className="flex items-center gap-2 mt-2">
          <Badge variant="outline" className="font-mono text-[10px] uppercase tracking-wider">
            {data.sector}
          </Badge>
          <span className="text-xs text-muted-foreground">Sector Analysis</span>
        </div>
      </div>

      {/* Hero Resilience Card */}
      <Card className="overflow-hidden border-none shadow-lg relative bg-slate-900 text-white group">
        {/* Subtle texture/noise overlay */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light"></div>
        <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
          <Shield className="w-32 h-32" />
        </div>
        
        <CardContent className="p-6 relative z-10">
          <div className="flex justify-between items-start mb-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest">Resilience Score</p>
                <Tooltip
                  content={
                    <div className="space-y-2">
                      <p className="font-semibold text-white">How we calculate this:</p>
                      <div className="space-y-1 text-slate-300">
                        <p>• <strong>35%</strong> Market Stability (inverse of volatility)</p>
                        <p>• <strong>25%</strong> Growth Potential (5-year forecast)</p>
                        <p>• <strong>20%</strong> Flood Safety</p>
                        <p>• <strong>20%</strong> Crime Safety</p>
                      </div>
                      <p className="text-slate-400 text-xs pt-1 border-t border-slate-700">
                        Higher scores indicate more resilient property values over time.
                      </p>
                    </div>
                  }
                >
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 cursor-help transition-colors" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-extrabold tracking-tighter">{resilience.score}</span>
                <span className="text-slate-500 font-medium">/100</span>
              </div>
            </div>
            <Badge 
              variant={getResilienceVariant(resilience.label)} 
              className={cn(
                "px-3 py-1 text-xs font-bold border-0 shadow-sm",
                resilience.label === 'High' ? "bg-emerald-500 text-white hover:bg-emerald-600" :
                resilience.label === 'Medium' ? "bg-amber-500 text-white hover:bg-amber-600" :
                "bg-rose-500 text-white hover:bg-rose-600"
              )}
            >
              {resilience.label}
            </Badge>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-300 flex items-center gap-2"><Activity className="w-3.5 h-3.5" /> Market Stability</span>
                <span className="text-white">{resilience.components.stability}%</span>
              </div>
              <Progress value={resilience.components.stability} className="h-1.5 bg-slate-800" indicatorClassName={getProgressColor(resilience.components.stability)} />
            </div>
            
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-300 flex items-center gap-2"><TrendingUp className="w-3.5 h-3.5" /> Growth Potential</span>
                <span className="text-white">{resilience.components.growth}%</span>
              </div>
              <Progress value={resilience.components.growth} className="h-1.5 bg-slate-800" indicatorClassName={getProgressColor(resilience.components.growth)} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Future Forecasts */}
      <section>
        <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          Valuation Forecast
        </h3>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-muted/40 rounded-lg border border-border/50">
            <span className="text-sm font-medium text-muted-foreground">Current Value</span>
            <span className="text-lg font-bold tracking-tight">{formatCurrency(current_valuation.value)}</span>
          </div>

          <div className="grid gap-2">
            {[1, 3, 5].map((year) => {
              const forecast = forecasts[`${year}y` as keyof typeof forecasts];
              return (
                <div key={year} className="flex items-center justify-between p-3 bg-card rounded-lg border shadow-sm transition-all hover:border-primary/20">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-8 h-8 rounded-full flex items-center justify-center bg-muted font-mono text-xs font-bold",
                      year === 5 && "bg-primary/10 text-primary"
                    )}>
                      {year}y
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs text-muted-foreground">Forecast</span>
                      <span className={cn(
                        "text-xs font-bold flex items-center gap-1",
                        forecast.growth_pct >= 0 ? "text-emerald-600" : "text-rose-600"
                      )}>
                        <TrendIndicator pct={forecast.growth_pct} />
                        {forecast.growth_pct > 0 ? '+' : ''}{forecast.growth_pct}%
                      </span>
                    </div>
                  </div>
                  <span className="font-semibold tabular-nums">{formatCurrency(forecast.price_value)}</span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <Separator />

      {/* Risk Factors */}
      <section>
        <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-primary" />
          Risk Assessment
        </h3>
        
        <div className="grid grid-cols-2 gap-3">
          {/* Flood Risk */}
          <div className="p-4 bg-card rounded-lg border shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-3">
              <span className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Droplets className="w-3.5 h-3.5" /> Flood Risk
              </span>
              <Badge variant={risk_factors.flood_risk_level === 'Low' ? 'outline' : 'destructive'} className="text-[10px] px-1.5 h-5">
                {risk_factors.flood_risk_level}
              </Badge>
            </div>
            <Progress value={resilience.components.flood_safety} className="h-1.5 mb-2" indicatorClassName={getProgressColor(resilience.components.flood_safety)} />
            <p className="text-[10px] text-right font-medium text-muted-foreground">{resilience.components.flood_safety}/100 Safety Score</p>
          </div>

          {/* Crime Safety */}
          <div className="p-4 bg-card rounded-lg border shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-3">
              <span className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5" /> Crime Safety
              </span>
              <Badge variant="outline" className="text-[10px] px-1.5 h-5 bg-background">
                Index: {Math.round(100 - resilience.components.crime_safety)}
              </Badge>
            </div>
            <Progress value={resilience.components.crime_safety} className="h-1.5 mb-2" indicatorClassName={getProgressColor(resilience.components.crime_safety)} />
            <p className="text-[10px] text-right font-medium text-muted-foreground">{resilience.components.crime_safety}/100 Safety Score</p>
          </div>
        </div>
      </section>
    </div>
  );
}