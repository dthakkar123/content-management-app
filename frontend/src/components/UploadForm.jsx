import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import api from '../services/api';
import { MAX_FILE_SIZE, ALLOWED_FILE_TYPES } from '../utils/constants';
import { formatFileSize } from '../utils/formatters';

const UploadForm = ({ onSuccess }) => {
  const [activeTab, setActiveTab] = useState('url'); // 'url' or 'file'
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  // Handle URL submission
  const handleURLSubmit = async (e) => {
    e.preventDefault();

    if (!url.trim()) {
      toast.error('Please enter a URL');
      return;
    }

    setLoading(true);
    const loadingToast = toast.loading('Processing URL...');

    try {
      const response = await api.content.submitURL(url);
      toast.success('Content processed successfully!', { id: loadingToast });
      setUrl('');
      if (onSuccess) onSuccess(response.data);
    } catch (error) {
      console.error('Error submitting URL:', error);
      toast.error(
        error.response?.data?.detail || 'Failed to process URL',
        { id: loadingToast }
      );
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload with dropzone
  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];

    if (!file) {
      toast.error('No file selected');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      toast.error(`File size exceeds ${formatFileSize(MAX_FILE_SIZE)}`);
      return;
    }

    setLoading(true);
    const loadingToast = toast.loading('Processing PDF...');

    try {
      const response = await api.content.uploadPDF(file);
      toast.success('PDF processed successfully!', { id: loadingToast });
      if (onSuccess) onSuccess(response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error(
        error.response?.data?.detail || 'Failed to process PDF',
        { id: loadingToast }
      );
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: loading,
  });

  return (
    <div className="card p-6">
      {/* Tab Headers */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('url')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'url'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Add URL
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'file'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Upload PDF
        </button>
      </div>

      {/* URL Tab */}
      {activeTab === 'url' && (
        <form onSubmit={handleURLSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://arxiv.org/abs/... or https://twitter.com/..."
              className="input w-full"
              disabled={loading}
            />
            <p className="mt-2 text-xs text-gray-500">
              Supports: Twitter threads, arXiv papers, ACM Digital Library, and web articles
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Add Content'}
          </button>
        </form>
      )}

      {/* File Upload Tab */}
      {activeTab === 'file' && (
        <div>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />

            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            <p className="mt-4 text-sm text-gray-600">
              {isDragActive ? (
                <span className="font-medium text-primary-600">Drop the PDF here</span>
              ) : (
                <>
                  <span className="font-medium text-primary-600">Click to upload</span> or
                  drag and drop
                </>
              )}
            </p>
            <p className="mt-1 text-xs text-gray-500">
              PDF files only (max {formatFileSize(MAX_FILE_SIZE)})
            </p>
          </div>

          {loading && (
            <div className="mt-4 flex items-center justify-center">
              <div className="w-6 h-6 border-3 border-primary-600 border-t-transparent rounded-full animate-spin" />
              <span className="ml-3 text-sm text-gray-600">Processing PDF...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadForm;
