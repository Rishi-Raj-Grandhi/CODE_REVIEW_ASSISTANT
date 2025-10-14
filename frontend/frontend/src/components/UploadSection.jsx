import { useState } from 'react';
import '../styles/UploadSection.css';

export default function UploadSection({ onSuccess, onError }) {
  const [uploading, setUploading] = useState(false);
  const BASE_URL = "http://127.0.0.1:8000";

  const handleUpload = async (file, type) => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    
    if (type === 'files') {
      Array.from(file).forEach(f => formData.append('files', f));
    } else if (type === 'folder') {
      // change field name to match FastAPI endpoint
      formData.append('zip_file', file);
    } else {
      formData.append('file', file);
    }

    try {
      const endpoint =
        type === "folder"
          ? `${BASE_URL}/upload/folder/`
          : type === "files"
          ? `${BASE_URL}/upload/files/`
          : `${BASE_URL}/upload/file/`;
      
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
              onChange={(e) => handleUpload(e.target.files[0], 'file')}
              disabled={uploading}
              accept=".py,.js,.jsx,.ts,.tsx,.java,.cpp,.c,.go,.rb,.php,.cs"
            />
          </label>

          <label className="upload-card multiple">
            <div className="icon">📁</div>
            <span>Multiple Files</span>
            <input
              type="file"
              multiple
              onChange={(e) => handleUpload(e.target.files, 'files')}
              disabled={uploading}
            />
          </label>

          <label className="upload-card folder">
            <div className="icon">📦</div>
            <span>ZIP Folder</span>
            <input
              type="file"
              accept=".zip"
              onChange={(e) => handleUpload(e.target.files[0], 'folder')}
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
