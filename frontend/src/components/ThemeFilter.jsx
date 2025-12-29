import { useState, useEffect, useRef } from 'react';

const ThemeFilter = ({ themes, selectedThemeIds, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleThemeToggle = (themeId) => {
    const newSelection = selectedThemeIds.includes(themeId)
      ? selectedThemeIds.filter((id) => id !== themeId)
      : [...selectedThemeIds, themeId];
    onChange(newSelection);
  };

  const handleClearAll = () => {
    onChange([]);
  };

  const selectedThemes = themes.filter((theme) =>
    selectedThemeIds.includes(theme.id)
  );

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn-secondary flex items-center space-x-2"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
        <span>
          {selectedThemeIds.length > 0
            ? `${selectedThemeIds.length} theme${selectedThemeIds.length > 1 ? 's' : ''}`
            : 'Filter by theme'}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Selected Themes Pills */}
      {selectedThemes.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {selectedThemes.map((theme) => (
            <span
              key={theme.id}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
              style={{
                backgroundColor: theme.color + '20',
                color: theme.color,
              }}
            >
              {theme.name}
              <button
                onClick={() => handleThemeToggle(theme.id)}
                className="ml-2 hover:opacity-70"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-10 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 max-h-80 overflow-y-auto">
          <div className="p-2">
            {/* Clear All */}
            {selectedThemeIds.length > 0 && (
              <button
                onClick={handleClearAll}
                className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded"
              >
                Clear all filters
              </button>
            )}

            {/* Theme List */}
            {themes.length === 0 ? (
              <p className="px-3 py-4 text-sm text-gray-500 text-center">
                No themes available
              </p>
            ) : (
              themes.map((theme) => (
                <label
                  key={theme.id}
                  className="flex items-center px-3 py-2 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedThemeIds.includes(theme.id)}
                    onChange={() => handleThemeToggle(theme.id)}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="ml-3 flex items-center space-x-2 flex-1">
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: theme.color }}
                    />
                    <span className="text-sm text-gray-700 truncate">
                      {theme.name}
                    </span>
                    <span className="text-xs text-gray-500 ml-auto">
                      ({theme.content_count})
                    </span>
                  </span>
                </label>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ThemeFilter;
