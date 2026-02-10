import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface GroupedBarChartProps {
  data: Array<{
    label: string;
    groups: { [key: string]: number };
  }>;
  height?: number;
  groupColors?: { [key: string]: string };
}

const DEFAULT_COLORS = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export default function GroupedBarChart({ 
  data, 
  height = 350,
  groupColors
}: GroupedBarChartProps) {
  
  // Get all unique group keys
  const groupKeys = data.length > 0 
    ? Object.keys(data[0].groups) 
    : [];

  // Format data for Recharts
  const chartData = data.map(item => ({
    name: item.label,
    ...Object.entries(item.groups).reduce((acc, [key, value]) => ({
      ...acc,
      [key]: value
    }), {})
  }));

  const colors = groupColors || groupKeys.reduce((acc, key, idx) => ({
    ...acc,
    [key]: DEFAULT_COLORS[idx % DEFAULT_COLORS.length]
  }), {});

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-3 py-2 border border-gray-200 rounded shadow-lg">
          <p className="text-sm font-medium text-gray-800 mb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm text-gray-600">
              <span style={{ color: entry.color }}>●</span> {entry.name}: {Math.round(entry.value * 100)}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis 
          type="number" 
          domain={[0, 1]}
          tickFormatter={(value) => `${Math.round(value * 100)}%`}
        />
        <YAxis 
          dataKey="name" 
          type="category" 
          width={150}
          tick={{ fontSize: 13 }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend 
          wrapperStyle={{ paddingTop: '20px' }}
          iconType="circle"
        />
        {groupKeys.map((key) => (
          <Bar 
            key={key}
            dataKey={key} 
            fill={colors[key as keyof typeof colors]} 
            radius={[0, 4, 4, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
