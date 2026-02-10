import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts';

interface VanWestendorpChartProps {
  data: {
    too_cheap_curve: number[][];
    good_value_curve: number[][];
    expensive_curve: number[][];
    too_expensive_curve: number[][];
    optimal_price_point: number;
    point_marginal_cheapness?: number;
    point_marginal_expensiveness?: number;
    indifference_price_point?: number;
    acceptable_range: {
      low: number;
      high: number;
    };
  };
  height?: number;
}

export default function VanWestendorpChart({ data, height = 400 }: VanWestendorpChartProps) {
  // Combine all curves into chart data format
  const prices = data.too_cheap_curve.map(point => point[0]);
  
  const chartData = prices.map((price, idx) => ({
    price,
    too_cheap: data.too_cheap_curve[idx][1],
    good_value: data.good_value_curve[idx][1],
    expensive: data.expensive_curve[idx][1],
    too_expensive: data.too_expensive_curve[idx][1]
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-3 py-2 border border-gray-200 rounded shadow-lg">
          <p className="text-sm font-medium text-gray-800 mb-1">${label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-xs text-gray-600">
              <span style={{ color: entry.color }}>●</span> {entry.name}: {Math.round(entry.value * 100)}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="price"
            tickFormatter={(value) => `$${value}`}
            label={{ value: 'Price', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            tickFormatter={(value) => `${Math.round(value * 100)}%`}
            label={{ value: 'Cumulative %', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '10px' }}
            iconType="line"
          />
          <Line 
            type="monotone" 
            dataKey="too_cheap" 
            stroke="#EF4444" 
            name="Too Cheap" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="good_value" 
            stroke="#10B981" 
            name="Good Value" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="expensive" 
            stroke="#F59E0B" 
            name="Expensive" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="too_expensive" 
            stroke="#DC2626" 
            name="Too Expensive" 
            strokeWidth={2}
            dot={false}
          />
          
          {/* Mark optimal price point */}
          <ReferenceDot 
            x={data.optimal_price_point} 
            y={0.5} 
            r={6} 
            fill="#2563EB" 
            stroke="#fff"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Key Insights */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-sm font-medium text-blue-900 mb-1">
            Optimal Price Point (OPP)
          </div>
          <div className="text-2xl font-bold text-blue-700">
            ${data.optimal_price_point}
          </div>
          <p className="text-xs text-blue-600 mt-1">
            Intersection of "Too Expensive" & "Too Cheap"
          </p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-sm font-medium text-green-900 mb-1">
            Acceptable Range
          </div>
          <div className="text-2xl font-bold text-green-700">
            ${data.acceptable_range.low} - ${data.acceptable_range.high}
          </div>
          <p className="text-xs text-green-600 mt-1">
            Between Point of Marginal Cheapness & Expensiveness
          </p>
        </div>

        {data.indifference_price_point && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="text-sm font-medium text-purple-900 mb-1">
              Indifference Price Point (IPP)
            </div>
            <div className="text-2xl font-bold text-purple-700">
              ${data.indifference_price_point}
            </div>
            <p className="text-xs text-purple-600 mt-1">
              Intersection of "Expensive" & "Good Value"
            </p>
          </div>
        )}

        {data.point_marginal_cheapness && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="text-sm font-medium text-amber-900 mb-1">
              Point of Marginal Cheapness (PMC)
            </div>
            <div className="text-2xl font-bold text-amber-700">
              ${data.point_marginal_cheapness}
            </div>
            <p className="text-xs text-amber-600 mt-1">
              Intersection of "Too Cheap" & "Good Value"
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
