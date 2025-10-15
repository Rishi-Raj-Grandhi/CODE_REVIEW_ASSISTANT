import { useState, useEffect } from 'react';
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
  const [showHistory, setShowHistory] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [isHistoricalView, setIsHistoricalView] = useState(false);
  
  const username = sessionStorage.getItem('username') || 'User';
  const userId = sessionStorage.getItem('userid');

  const handleUploadSuccess = (data) => {
    setReviewData(data);
    setError(null);
    setIsHistoricalView(false);
  };

  const handleUploadError = (err) => {
    setError(err);
  };

  const handleReset = () => {
    setReviewData(null);
    setError(null);
    setIsHistoricalView(false);
  };

  // Fetch user's upload history
  const fetchHistory = async () => {
    if (!userId) {
      setError('User ID not found');
      return;
    }

    setLoadingHistory(true);
    try {
      const formData = new FormData();
      formData.append('user_id', userId);

      const response = await fetch('http://localhost:8000/user/uploads/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }

      const result = await response.json();
      if (result.status === 'success' && result.data) {
        setHistoryData(result.data);
        setShowHistory(true);
      } else {
        setError('No history found');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSelectHistory = (record) => {
    setReviewData(record.result);
    setShowHistory(false);
    setIsHistoricalView(true);
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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
          {userId && (
            <button 
              className="history-btn" 
              onClick={fetchHistory}
              disabled={loadingHistory}
            >
              {loadingHistory ? '⏳ Loading...' : '🕒 View Past Reviews'}
            </button>
          )}
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
          {isHistoricalView && (
            <div className="historical-badge">
              📜 Viewing Historical Review
            </div>
          )}
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

      {/* History Modal */}
      {showHistory && (
        <div className="history-modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="history-modal" onClick={(e) => e.stopPropagation()}>
            <div className="history-modal-header">
              <h2>🕒 Review History</h2>
              <button 
                className="close-modal-btn" 
                onClick={() => setShowHistory(false)}
              >
                ×
              </button>
            </div>
            <div className="history-modal-content">
              {historyData.length > 0 ? (
                <div className="history-list">
                  {historyData.map((record, index) => (
                    <div 
                      key={index} 
                      className="history-item"
                      onClick={() => handleSelectHistory(record)}
                    >
                      <div className="history-item-header">
                        <span className="history-type">
                          {record.upload_type === 'zip' ? '📦 ZIP' : '📄 File'}
                        </span>
                        <span className="history-date">
                          {formatDate(record.timestamp)}
                        </span>
                      </div>
                      <div className="history-item-stats">
                        <span>Files: {record.result.metadata.total_files_reviewed}</span>
                        <span>Score: {record.result.summary.average_score.toFixed(1)}</span>
                        <span>Issues: {record.result.summary.total_issues_found}</span>
                      </div>
                      <div className="history-item-recommendation">
                        {record.result.summary.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-history">
                  <p>No previous reviews found</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}