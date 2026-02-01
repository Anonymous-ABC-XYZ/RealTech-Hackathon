'use client';

import { useState } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, Cell 
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { TrendingUp, Shield, Droplets, Lock, BarChart3 } from 'lucide-react';

interface SavedLocation {
  id: string;
  address: string;
  lat: number;
  lng: number;
  color: string;
}

interface ComparisonChartProps {
  savedLocations: SavedLocation[];
  comparisonData: any[];
}

type ChartType = 'price' | 'resilience' | 'stability' | 'growth' | 'flood' | 'crime';

const chartOptions: { value: ChartType; label: string; icon: React.ReactNode }[] = [
  { value: 'price', label: 'Price Forecast', icon: <TrendingUp className="w-4 h-4" /> },
  { value: 'resilience', label: 'Resilience Score', icon: <Shield className="w-4 h-4" /> },
  { value: 'stability', label: 'Stability', icon: <BarChart3 className="w-4 h-4" /> },
  { value: 'growth', label: 'Growth', icon: <TrendingUp className="w-4 h-4" /> },
  { value: 'flood', label: 'Flood Safety', icon: <Droplets className="w-4 h-4" /> },
  { value: 'crime', label: 'Crime Safety', icon: <Lock className="w-4 h-4" /> },
];

export default function ComparisonChart({ savedLocations, comparisonData }: ComparisonChartProps) {
  const [selectedChart, setSelectedChart] = useState<ChartType>('price');

  // Only use locations that have actual comparison data
  const locationsWithData = savedLocations.filter((_, idx) => comparisonData[idx] != null);

  // Prepare data for price forecast line chart
  const getPriceData = () => {
    const years = ['Current', '1 Year', '3 Years', '5 Years'];
    return years.map((year, idx) => {
      const dataPoint: any = { year };
      locationsWithData.forEach((loc) => {
        const locIdx = savedLocations.findIndex(l => l.id === loc.id);
        const data = comparisonData[locIdx];
        if (data) {
          const currentPrice = data.current_valuation?.value || 450000;
          if (idx === 0) {
            dataPoint[loc.address.substring(0, 15)] = currentPrice;
          } else if (idx === 1) {
            dataPoint[loc.address.substring(0, 15)] = data.forecasts?.['1y']?.price_value || currentPrice * 1.025;
          } else if (idx === 2) {
            dataPoint[loc.address.substring(0, 15)] = data.forecasts?.['3y']?.price_value || currentPrice * 1.08;
          } else {
            dataPoint[loc.address.substring(0, 15)] = data.forecasts?.['5y']?.price_value || currentPrice * 1.15;
          }
        }
      });
      return dataPoint;
    });
  };

  // Prepare data for bar charts
  const getBarData = (type: ChartType) => {
    return locationsWithData.map((loc, index) => {
      const locIdx = savedLocations.findIndex(l => l.id === loc.id);
      const data = comparisonData[locIdx];
      let value = 0;
      
      if (data) {
        switch (type) {
          case 'resilience':
            value = data.resilience?.score || 0;
            break;
          case 'stability':
            value = data.resilience?.components?.stability || 0;
            break;
          case 'growth':
            value = data.resilience?.components?.growth || 0;
            break;
          case 'flood':
            value = data.resilience?.components?.flood_safety || 0;
            break;
          case 'crime':
            value = data.resilience?.components?.crime_safety || 0;
            break;
        }
      }
      
      return {
        name: `${index + 1}`,
        fullAddress: loc.address,
        value,
        color: loc.color,
      };
    });
  };

  const getYAxisConfig = () => {
    switch (selectedChart) {
      case 'price':
        return { domain: ['auto', 'auto'], tickFormatter: (v: number) => `£${(v / 1000).toFixed(0)}k` };
      case 'resilience':
      case 'stability':
      case 'growth':
      case 'flood':
      case 'crime':
        return { domain: [0, 100], tickFormatter: (v: number) => `${v}` };
      default:
        return { domain: ['auto', 'auto'], tickFormatter: (v: number) => `${v}` };
    }
  };

  const getYAxisLabel = () => {
    switch (selectedChart) {
      case 'price':
        return 'Price (£)';
      case 'resilience':
        return 'Resilience Score';
      case 'stability':
        return 'Stability Score';
      case 'growth':
        return 'Growth Score';
      case 'flood':
        return 'Flood Safety Score';
      case 'crime':
        return 'Crime Safety Score';
      default:
        return '';
    }
  };

  const yAxisConfig = getYAxisConfig();

  return (
    <Card className="p-4 mb-4">
      {/* Chart Type Selector */}
      <div className="flex flex-wrap gap-2 mb-4">
        {chartOptions.map((option) => (
          <Button
            key={option.value}
            variant={selectedChart === option.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedChart(option.value)}
            className="text-xs"
          >
            {option.icon}
            <span className="ml-1.5">{option.label}</span>
          </Button>
        ))}
      </div>

      {/* Chart Container */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {selectedChart === 'price' ? (
            <LineChart data={getPriceData()} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="year" 
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                axisLine={{ stroke: '#374151' }}
              />
              <YAxis 
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                tickFormatter={yAxisConfig.tickFormatter}
                axisLine={{ stroke: '#374151' }}
                label={{ value: getYAxisLabel(), angle: -90, position: 'insideLeft', fontSize: 10, fill: '#9ca3af' }}
              />
              <Tooltip 
                formatter={(value) => [`£${Number(value).toLocaleString()}`, '']}
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} />
              {locationsWithData.map((loc) => (
                <Line
                  key={loc.id}
                  type="monotone"
                  dataKey={loc.address.substring(0, 15)}
                  stroke={loc.color}
                  strokeWidth={2}
                  dot={{ r: 4, fill: loc.color }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          ) : (
            <BarChart data={getBarData(selectedChart)} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                axisLine={{ stroke: '#374151' }}
                interval={0}
              />
              <YAxis 
                domain={yAxisConfig.domain as [number, number]}
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                tickFormatter={yAxisConfig.tickFormatter}
                axisLine={{ stroke: '#374151' }}
                label={{ value: getYAxisLabel(), angle: -90, position: 'insideLeft', fontSize: 10, fill: '#9ca3af' }}
              />
              <Tooltip 
                formatter={(value, name, props) => [`${Number(value).toFixed(1)}`, getYAxisLabel()]}
                labelFormatter={(label, payload) => {
                  if (payload && payload[0]) {
                    return payload[0].payload.fullAddress;
                  }
                  return label;
                }}
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '6px', padding: '6px 10px', fontSize: '11px' }}
                labelStyle={{ color: '#f3f4f6', fontSize: '10px', marginBottom: '2px' }}
                itemStyle={{ color: '#f3f4f6', fontSize: '11px', padding: 0 }}
              />
              <Bar 
                dataKey="value" 
                radius={[4, 4, 0, 0]}
              >
                {getBarData(selectedChart).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
