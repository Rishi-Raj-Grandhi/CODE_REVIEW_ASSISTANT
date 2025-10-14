import { useState } from 'react';
import '../styles/IssuesFeed.css';

export default function IssuesFeed({ files }) {
  const [filter, setFilter] = useState('all');

  const allIssues = files
    .flatMap((file) =>
      file.issues.map((issue) => ({
        ...issue,
        filename: file.filename,
        file_path: file.file_path,
      }))
    )
    .sort((a, b) => {
      const severityRank = { Critical: 0, Major: 1, Minor: 2 };
      return severityRank[a.severity] - severityRank[b.severity];
    });

  const filteredIssues =
    filter === 'all'
      ? allIssues
      : allIssues.filter((issue) => issue.severity === filter);

  const getSeverityClass = (severity) => {
    return severity.toLowerCase().replace(' ', '-');
  };

  const criticalCount = allIssues.filter((i) => i.severity === 'Critical').length;
  const majorCount = allIssues.filter((i) => i.severity === 'Major').length;

  return (
    <div className="issues-feed-container">
      <div className="feed-header">
        <h3>⚠️ Issues & Recommendations</h3>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({allIssues.length})
          </button>
          <button
            className={`filter-btn ${filter === 'Critical' ? 'active' : ''}`}
            onClick={() => setFilter('Critical')}
          >
            Critical ({criticalCount})
          </button>
          <button
            className={`filter-btn ${filter === 'Major' ? 'active' : ''}`}
            onClick={() => setFilter('Major')}
          >
            Major ({majorCount})
          </button>
        </div>
      </div>

      <div className="issues-list">
        {filteredIssues.length === 0 ? (
          <div className="no-issues">✅ No issues in this category</div>
        ) : (
          filteredIssues.map((issue, idx) => (
            <div
              key={idx}
              className={`issue-card ${getSeverityClass(issue.severity)}`}
            >
              <div className="issue-header">
                <span className={`severity-badge ${getSeverityClass(issue.severity)}`}>
                  {issue.severity}
                </span>
                <span className="issue-type">{issue.type}</span>
              </div>
              <div className="issue-message">{issue.message}</div>
              <div className="issue-file">📍 {issue.filename}</div>
              <div className="issue-recommendation">
                <strong>💡 Fix:</strong> {issue.recommendation}
              </div>
              {issue.code_example && (
                <div className="code-example">
                  <code>{issue.code_example}</code>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}