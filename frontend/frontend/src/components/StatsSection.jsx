import '../styles/StatsSection.css';

export default function StatsSection({ summary }) {
  const stats = [
    {
      label: 'Overall Score',
      value: summary.average_score,
      color: 'score',
      suffix: '/100',
    },
    {
      label: 'Files Reviewed',
      value: summary.total_files,
      color: 'files',
    },
    {
      label: 'Issues Found',
      value: summary.total_issues_found,
      color: 'issues',
    },
    {
      label: 'Improvements',
      value: summary.total_improvements_suggested,
      color: 'improvements',
    },
  ];

  return (
    <div className="stats-section">
      {stats.map((stat, idx) => (
        <div key={idx} className={`stat-card ${stat.color}`}>
          <div className="stat-value">
            {stat.value}
            {stat.suffix && <span className="suffix">{stat.suffix}</span>}
          </div>
          <div className="stat-label">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}