import { useState } from 'react';
import '../styles/UploadSection.css';

export default function UploadSection({ onSuccess, onError }) {
  const [uploading, setUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadMode, setUploadMode] = useState(null);
  const BASE_URL = "http://127.0.0.1:8000";

  const handleFileSelect = (e, mode) => {
    if (mode === 'multiple') {
      setSelectedFiles(Array.from(e.target.files));
      setUploadMode('multiple');
    } else if (mode === 'single') {
      handleDirectUpload([e.target.files[0]], 'single');
    } else if (mode === 'folder') {
      handleDirectUpload([e.target.files[0]], 'folder');
    }
    e.target.value = '';
  };

  const handleDirectUpload = async (files, mode) => {
    setUploading(true);
    const formData = new FormData();

    try {
      // ✅ Add user_id from session storage
      const userId = sessionStorage.getItem('userid');
      if (!userId) throw new Error('User not logged in');
      formData.append('user_id', userId);

      let endpoint = `${BASE_URL}/upload/file/`;

      if (mode === 'single') {
        formData.append('file', files[0]);
      } else if (mode === 'folder') {
        formData.append('zip_file', files[0]);
        endpoint = `${BASE_URL}/upload/folder/`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();
      onSuccess(data);
    } catch (err) {
      onError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
    if (selectedFiles.length === 1) {
      setUploadMode(null);
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      onError('No files selected');
      return;
    }

    setUploading(true);
    const formData = new FormData();

    try {
      // ✅ Add user_id for multiple file upload
      const userId = sessionStorage.getItem('userId');
      if (!userId) throw new Error('User not logged in');
      formData.append('user_id', userId);

      selectedFiles.forEach((file) => formData.append('files', file));
      const endpoint = `${BASE_URL}/upload/files/`;

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();
      setSelectedFiles([]);
      setUploadMode(null);
      onSuccess(data);
    } catch (err) {
      onError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
      js: '📜', jsx: '⚛️', ts: '📘', tsx: '⚛️',
      py: '🐍', java: '☕', cpp: '⚙️', c: '⚙️',
      go: '🐹', rb: '💎', php: '🐘', cs: '🔷',
      json: '{}', yaml: '⚙️', html: '🌐', css: '🎨',
      zip: '📦', md: '📝'
    };
    return iconMap[ext] || '📄';
  };

  // Show file list ONLY for multiple files mode
  if (uploadMode === 'multiple' && selectedFiles.length > 0) {
    return (
      <div className="upload-section">
        <div className="upload-container">
          <div className="upload-header">
            <h2>Review Files</h2>
            <p>Ready to analyze {selectedFiles.length} file(s)</p>
          </div>

          <div className="files-selected-container">
            <div className="files-list-selected">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="file-item-selected">
                  <span className="file-icon">{getFileIcon(file.name)}</span>
                  <div className="file-info">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">
                      {(file.size / 1024).toFixed(2)} KB
                    </span>
                  </div>
                  <button
                    className="remove-btn"
                    onClick={() => removeFile(idx)}
                    disabled={uploading}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>

            <div className="upload-actions">
              <button
                className="upload-btn"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? (
                  <>
                    <span className="spinner-small"></span>
                    Analyzing...
                  </>
                ) : (
                  '▶ Generate Review'
                )}
              </button>
              <button
                className="cancel-btn"
                onClick={() => {
                  setSelectedFiles([]);
                  setUploadMode(null);
                }}
                disabled={uploading}
              >
                ✕ Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="upload-section">
      <div className="upload-container">
        <div className="upload-header">
          <h2>Start Your Code Review</h2>
          <p>Upload your code for comprehensive AI-powered analysis</p>
        </div>

        <div className="upload-options">
          <label className="upload-card single">
            <div className="icon">📄</div>
            <span>Single File</span>
            <input
              type="file"
              onChange={(e) => handleFileSelect(e, 'single')}
              disabled={uploading}
              accept=".py,.js,.jsx,.ts,.tsx,.java,.cpp,.c,.go,.rb,.php,.cs,.json,.yaml,.html,.css"
            />
          </label>

          <label className="upload-card multiple">
            <div className="icon">📁</div>
            <span>Multiple Files</span>
            <input
              type="file"
              multiple
              onChange={(e) => handleFileSelect(e, 'multiple')}
              disabled={uploading}
            />
          </label>

          <label className="upload-card folder">
            <div className="icon">📦</div>
            <span>ZIP Folder</span>
            <input
              type="file"
              accept=".zip"
              onChange={(e) => handleFileSelect(e, 'folder')}
              disabled={uploading}
            />
          </label>
        </div>

        {uploading && (
          <div className="uploading-state">
            <div className="spinner"></div>
            <p>Analyzing your code...</p>
          </div>
        )}
      </div>
    </div>
  );
}
