import { useState } from 'react';
import UploadSection from './components/UploadSection';
import StatsSection from './components/StatsSection';
import IssuesChart from './components/IssuesChart';
import FilesList from './components/FilesList';
import IssuesFeed from './components/IssuesFeed';
import './styles/Dashboard.css';

export default function Dashboard({ onLogout }) {
  const [reviewData, setReviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const username = sessionStorage.getItem('username') || 'User';

  const handleUploadSuccess = (data) => {
    setReviewData(data);
    setError(null);
  };

  const handleUploadError = (err) => {
    setError(err);
  };

  const handleReset = () => {
    setReviewData(null);
    setError(null);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>📋 CODE REVIEWER ASSISTANT</h1>
          <p>Automated code quality analysis powered by AI</p>
        </div>
        <div className="user-section">
          <span className="username">👤 {username}</span>
          <button className="logout-btn" onClick={onLogout}>
            Logout
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {!reviewData ? (
        <UploadSection onSuccess={handleUploadSuccess} onError={handleUploadError} />
      ) : (
        <div className="results-container">
          <button className="reset-btn" onClick={handleReset}>
            ↻ Review Another Project
          </button>

          <StatsSection summary={reviewData.summary} />

          <div className="content-grid">
            <div className="chart-card">
              <IssuesChart distribution={reviewData.summary.issue_distribution} />
            </div>

            <div className="files-card">
              <FilesList files={reviewData.files} />
            </div>
          </div>

          <div className="issues-card">
            <IssuesFeed files={reviewData.files} />
          </div>
        </div>
      )}
    </div>
  );
}