import { useState, useEffect } from 'react';
import { useContent } from '../hooks/useContent';
import { useThemes } from '../hooks/useThemes';
import { useSearch } from '../hooks/useSearch';
import UploadForm from '../components/UploadForm';
import ContentGrid from '../components/ContentGrid';
import SearchBar from '../components/SearchBar';
import ThemeFilter from '../components/ThemeFilter';

const HomePage = () => {
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [activeView, setActiveView] = useState('recent'); // 'recent' or 'search'
  const [selectedThemeIds, setSelectedThemeIds] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const { themes } = useThemes();
  const { content, loading, error, refetch } = useContent();
  const {
    results: searchResults,
    loading: searchLoading,
    search,
  } = useSearch();

  // Trigger search when filters change
  useEffect(() => {
    if (activeView === 'search' && (searchQuery || selectedThemeIds.length > 0)) {
      search({
        q: searchQuery,
        theme_ids: selectedThemeIds,
        page: 1,
      });
    }
  }, [searchQuery, selectedThemeIds, activeView, search]);

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query || selectedThemeIds.length > 0) {
      setActiveView('search');
    } else {
      setActiveView('recent');
    }
  };

  const handleThemeFilterChange = (themeIds) => {
    setSelectedThemeIds(themeIds);
    if (themeIds.length > 0 || searchQuery) {
      setActiveView('search');
    } else {
      setActiveView('recent');
    }
  };

  const handleUploadSuccess = () => {
    setShowUploadForm(false);
    refetch();
    setActiveView('recent');
    setSearchQuery('');
    setSelectedThemeIds([]);
  };

  const displayContent = activeView === 'search' ? searchResults : content;
  const displayLoading = activeView === 'search' ? searchLoading : loading;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl font-bold mb-3">Content Management & Summarization</h1>
          <p className="text-xl text-primary-100">
            AI-powered insights for your research and reading
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="btn-primary inline-flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Add Content
          </button>
        </div>

        {/* Upload Form (Collapsible) */}
        {showUploadForm && (
          <div className="mb-8">
            <UploadForm onSuccess={handleUploadSuccess} />
          </div>
        )}

        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} initialValue={searchQuery} />
            </div>
            <ThemeFilter
              themes={themes}
              selectedThemeIds={selectedThemeIds}
              onChange={handleThemeFilterChange}
            />
          </div>

          {/* Active Filters Display */}
          {(searchQuery || selectedThemeIds.length > 0) && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                {activeView === 'search' && (
                  <>
                    Showing search results
                    {searchQuery && <span className="font-medium"> for "{searchQuery}"</span>}
                  </>
                )}
              </p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedThemeIds([]);
                  setActiveView('recent');
                }}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>

        {/* View Toggle */}
        <div className="mb-6 border-b border-gray-200">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveView('recent')}
              className={`pb-3 border-b-2 transition-colors ${
                activeView === 'recent'
                  ? 'border-primary-600 text-primary-600 font-medium'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Recent Content
            </button>
            {(searchQuery || selectedThemeIds.length > 0) && (
              <button
                onClick={() => setActiveView('search')}
                className={`pb-3 border-b-2 transition-colors ${
                  activeView === 'search'
                    ? 'border-primary-600 text-primary-600 font-medium'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Search Results
              </button>
            )}
          </div>
        </div>

        {/* Content Grid */}
        <ContentGrid items={displayContent} loading={displayLoading} error={error} />

        {/* Empty State for New Users */}
        {!displayLoading && !error && displayContent.length === 0 && activeView === 'recent' && (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary-100 mb-6">
              <svg
                className="w-10 h-10 text-primary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Welcome to your Content Library
            </h2>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Add your first piece of content by clicking the "Add Content" button above.
              Support for Twitter threads, research papers, PDFs, and web articles.
            </p>
            <button
              onClick={() => setShowUploadForm(true)}
              className="btn-primary inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Get Started
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
