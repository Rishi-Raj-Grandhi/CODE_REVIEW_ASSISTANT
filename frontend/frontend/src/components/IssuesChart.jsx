import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import '../styles/IssuesChart.css';

const COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B4D6', '#A8E6CF',
  '#FFD3B6', '#FFAAA5', '#AA96DA', '#FCBAD3', '#A8D8EA',
  '#FF8B94', '#73C6B6', '#F9F3EE', '#CDB5D4', '#FFC4D6'
];

export default function IssuesChart({ distribution }) {
  const data = Object.entries(distribution).map(([name, value]) => ({
    name,
    value,
  }));

  if (!data.length) {
    return (
      <div className="chart-empty">
        <p>✅ No issues found!</p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3>Issue Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}