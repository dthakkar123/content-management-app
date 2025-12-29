import { Link } from 'react-router-dom';
import { formatRelativeTime, truncateText } from '../utils/formatters';
import { SOURCE_TYPE_LABELS, SOURCE_TYPE_COLORS } from '../utils/constants';

const ContentCard = ({ content }) => {
  const {
    id,
    title,
    author,
    source_type,
    source_url,
    created_at,
    summary_preview,
    themes = [],
  } = content;

  return (
    <Link to={`/content/${id}`} className="block">
      <div className="card p-6 h-full hover:border-primary-300 border-2 border-transparent transition-all">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
              {title}
            </h3>
            {author && (
              <p className="text-sm text-gray-600 truncate">by {author}</p>
            )}
          </div>
          <span
            className={`badge ml-3 flex-shrink-0 ${
              SOURCE_TYPE_COLORS[source_type] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {SOURCE_TYPE_LABELS[source_type] || source_type}
          </span>
        </div>

        {/* Summary Preview */}
        {summary_preview && (
          <p className="text-gray-700 text-sm mb-4 line-clamp-3">
            {summary_preview}
          </p>
        )}

        {/* Themes */}
        {themes.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {themes.slice(0, 3).map((theme) => (
              <span
                key={theme.theme_id}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                style={{
                  backgroundColor: theme.color + '20',
                  color: theme.color,
                }}
              >
                {theme.theme_name}
              </span>
            ))}
            {themes.length > 3 && (
              <span className="text-xs text-gray-500 self-center">
                +{themes.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 mt-auto pt-3 border-t border-gray-100">
          <span>{formatRelativeTime(created_at)}</span>
          {source_url && (
            <span className="text-primary-600 hover:text-primary-700 font-medium">
              View details →
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default ContentCard;
