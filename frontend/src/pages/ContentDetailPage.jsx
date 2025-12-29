import { useParams, Link, useNavigate } from 'react-router-dom';
import { useContentDetail } from '../hooks/useContent';
import { formatDateTime, formatRelativeTime } from '../utils/formatters';
import { SOURCE_TYPE_LABELS } from '../utils/constants';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import api from '../services/api';

const ContentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { content, loading, error } = useContentDetail(id);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this content?')) {
      return;
    }

    try {
      await api.content.delete(id);
      toast.success('Content deleted successfully');
      navigate('/');
    } catch (error) {
      console.error('Error deleting content:', error);
      toast.error('Failed to delete content');
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading content..." />;
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Content not found</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link to="/" className="btn-primary">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  if (!content) {
    return null;
  }

  const { summary, themes = [] } = content;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Link
            to="/"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Home
          </Link>

          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <span className="badge bg-primary-100 text-primary-800">
                  {SOURCE_TYPE_LABELS[content.source_type] || content.source_type}
                </span>
                <span className="text-sm text-gray-500">
                  {formatRelativeTime(content.created_at)}
                </span>
              </div>

              <h1 className="text-3xl font-bold text-gray-900 mb-3">{content.title}</h1>

              {content.author && (
                <p className="text-lg text-gray-600 mb-2">by {content.author}</p>
              )}

              {content.publish_date && (
                <p className="text-sm text-gray-500">
                  Published {formatDateTime(content.publish_date)}
                </p>
              )}
            </div>

            <button
              onClick={handleDelete}
              className="btn-danger ml-4 flex-shrink-0"
              title="Delete content"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Themes */}
        {themes.length > 0 && (
          <div className="mb-8">
            <h2 className="text-sm font-medium text-gray-700 mb-3">Themes</h2>
            <div className="flex flex-wrap gap-2">
              {themes.map((theme) => (
                <span
                  key={theme.theme_id}
                  className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium"
                  style={{
                    backgroundColor: theme.color + '20',
                    color: theme.color,
                  }}
                >
                  {theme.theme_name}
                  {theme.confidence && (
                    <span className="ml-2 text-xs opacity-75">
                      {Math.round(theme.confidence * 100)}%
                    </span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Source Link */}
        {content.source_url && (
          <div className="mb-8">
            <a
              href={content.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-primary-600 hover:text-primary-700"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
              View original source
            </a>
          </div>
        )}

        {/* Summary */}
        {summary ? (
          <div className="space-y-8">
            {/* Overview */}
            <section className="card p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Overview</h2>
              <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                {summary.overview}
              </div>
            </section>

            {/* Key Insights */}
            {summary.key_insights && summary.key_insights.length > 0 && (
              <section className="card p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Key Insights</h2>
                <ul className="space-y-3">
                  {summary.key_insights.map((insight, index) => (
                    <li key={index} className="flex items-start">
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-700 font-semibold text-sm mr-3 flex-shrink-0 mt-0.5">
                        {index + 1}
                      </span>
                      <span className="text-gray-700 flex-1">{insight}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Implications */}
            {summary.implications && (
              <section className="card p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Implications & Discussion
                </h2>
                <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                  {summary.implications}
                </div>
              </section>
            )}
          </div>
        ) : (
          <div className="card p-6 text-center">
            <p className="text-gray-500">No summary available for this content.</p>
          </div>
        )}

        {/* Metadata (Expandable) */}
        {content.extraction_metadata && Object.keys(content.extraction_metadata).length > 0 && (
          <details className="mt-8 card p-6">
            <summary className="cursor-pointer font-semibold text-gray-900 hover:text-gray-700">
              Technical Metadata
            </summary>
            <pre className="mt-4 text-xs text-gray-600 overflow-x-auto bg-gray-50 p-4 rounded">
              {JSON.stringify(content.extraction_metadata, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};

export default ContentDetailPage;
