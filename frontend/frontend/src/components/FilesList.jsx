import { useState } from 'react';
import '../styles/FilesList.css';

export default function FilesList({ files }) {
  const [expandedFile, setExpandedFile] = useState(null);

  const getScoreColor = (score) => {
    if (score >= 85) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
  };

  return (
    <div className="files-list-container">
      <h3>📄 Reviewed Files</h3>
      <div className="files-list">
        {files.map((file, idx) => (
          <div
            key={idx}
            className={`file-item ${getScoreColor(file.file_score.overall)}`}
            onClick={() => setExpandedFile(expandedFile === idx ? null : idx)}
          >
            <div className="file-header">
              <span className="file-name">{file.filename}</span>
              <span className={`file-score ${getScoreColor(file.file_score.overall)}`}>
                {file.file_score.overall}
              </span>
            </div>
            {expandedFile === idx && (
              <div className="file-details">
                <div className="detail-row">
                  <span>Maintainability</span>
                  <span>{file.file_score.maintainability}</span>
                </div>
                <div className="detail-row">
                  <span>Readability</span>
                  <span>{file.file_score.readability}</span>
                </div>
                <div className="detail-row">
                  <span>Robustness</span>
                  <span>{file.file_score.robustness}</span>
                </div>
                <div className="detail-row">
                  <span>Security</span>
                  <span>{file.file_score.security}</span>
                </div>
                <div className="detail-row">
                  <span>Performance</span>
                  <span>{file.file_score.performance}</span>
                </div>
                <div className="detail-row">
                  <span>Best Practices</span>
                  <span>{file.file_score.best_practices}</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}