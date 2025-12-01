import React, { useState } from 'react';
import axios from 'axios';

/**
 * FileUploader component for uploading documents
 */
const FileUploader = ({ chatId, chatName, onUploadSuccess, variant = 'full' }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setMessage('');
    setError('');
    
    // Auto-upload for icon variant
    if (variant === 'icon' && selectedFile) {
      uploadFile(selectedFile);
    }
  };

  const uploadFile = async (fileToUpload = file) => {
    if (!fileToUpload) {
      setError('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileToUpload);
    formData.append('chat_id', chatId);
    if (chatName) {
      formData.append('chat_name', chatName);
    }

    setUploading(true);
    setMessage('');
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage(`✓ ${response.data.message} (${response.data.chunks} chunks processed)`);
      setFile(null);
      
      // Reset file input
      const fileInput = document.getElementById(`file-input-${variant}`);
      if (fileInput) fileInput.value = '';

      // Notify parent component
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }

      // Clear success message after 5 seconds
      setTimeout(() => setMessage(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading file. Please try again.');
      setTimeout(() => setError(''), 5000);
    } finally {
      setUploading(false);
    }
  };

  const handleUpload = () => uploadFile();

  if (variant === 'icon') {
    return (
      <div className="relative">
        <input
          id="file-input-icon"
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          disabled={uploading}
          className="hidden"
        />
        <label
          htmlFor="file-input-icon"
          className={`flex items-center justify-center w-12 h-12 rounded-xl bg-gray-800 border border-gray-700 hover:border-blue-500 text-2xl cursor-pointer transition-all ${
            uploading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'
          }`}
          title="Upload document"
        >
          {uploading ? (
            <div className="w-5 h-5 border-2 border-gray-600 border-t-blue-500 rounded-full animate-spin" />
          ) : (
            '📎'
          )}
        </label>
        
        {(message || error) && (
          <div className={`absolute bottom-full left-0 mb-2 px-3 py-1.5 rounded-lg text-xs whitespace-nowrap ${
            error ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
          }`}>
            {message || error}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
        <span className="text-2xl">📁</span> Upload Document
      </h3>
      <p className="text-sm text-gray-400 mb-4">
        Upload PDF, DOCX, or TXT files to chat with your documents
      </p>
      
      <div className="flex gap-3">
        <input
          id="file-input-full"
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          disabled={uploading}
          className="flex-1 text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:cursor-pointer cursor-pointer"
        />
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
        >
          {uploading ? '⏳ Uploading...' : '📤 Upload'}
        </button>
      </div>

      {message && (
        <div className="mt-4 px-4 py-2 bg-green-500/20 border border-green-500/30 text-green-400 rounded-lg text-sm">
          {message}
        </div>
      )}
      {error && (
        <div className="mt-4 px-4 py-2 bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg text-sm">
          {error}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
