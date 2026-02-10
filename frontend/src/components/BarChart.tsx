import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface BarChartProps {
  data: Array<{
    label: string;
    value: number;
    percentage?: number;
  }>;
  height?: number;
  showPercentage?: boolean;
  color?: string;
  horizontal?: boolean;
}

export default function BarChart({ 
  data, 
  height = 300, 
  showPercentage = true, 
  color = '#2563EB',
  horizontal = true 
}: BarChartProps) {
  
  // Format data for Recharts
  const chartData = data.map(item => ({
    name: item.label,
    value: showPercentage ? (item.percentage || item.value) : item.value,
    displayValue: showPercentage 
      ? `${Math.round((item.percentage || item.value) * 100)}%` 
      : item.value.toString()
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-3 py-2 border border-gray-200 rounded shadow-lg">
          <p className="text-sm font-medium text-gray-800">{payload[0].payload.name}</p>
          <p className="text-sm text-gray-600">
            {payload[0].payload.displayValue}
          </p>
        </div>
      );
    }
    return null;
  };

  if (horizontal) {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            type="number" 
            domain={[0, showPercentage ? 1 : 'auto']}
            tickFormatter={(value) => showPercentage ? `${Math.round(value * 100)}%` : value.toString()}
          />
          <YAxis 
            dataKey="name" 
            type="category" 
            width={150}
            tick={{ fontSize: 13 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" fill={color} radius={[0, 4, 4, 0]} />
        </RechartsBarChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart
        data={chartData}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis 
          dataKey="name"
          tick={{ fontSize: 13 }}
        />
        <YAxis 
          domain={[0, showPercentage ? 1 : 'auto']}
          tickFormatter={(value) => showPercentage ? `${Math.round(value * 100)}%` : value.toString()}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}
