import { useState, useCallback } from 'react';
import api from '../services/api';

export const useSearch = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 0,
  });
  const [searchParams, setSearchParams] = useState({
    q: '',
    theme_ids: [],
    source_types: [],
    page: 1,
    page_size: 10,
  });

  const search = useCallback(async (params) => {
    setLoading(true);
    setError(null);

    const searchQuery = {
      q: '',
      theme_ids: [],
      source_types: [],
      page: 1,
      page_size: 10,
      ...params,
    };

    setSearchParams(searchQuery);

    try {
      // Convert arrays to comma-separated strings for API
      const apiParams = {
        q: searchQuery.q || undefined,
        theme_ids: searchQuery.theme_ids?.length
          ? searchQuery.theme_ids.join(',')
          : undefined,
        source_types: searchQuery.source_types?.length
          ? searchQuery.source_types.join(',')
          : undefined,
        page: searchQuery.page || 1,
        page_size: searchQuery.page_size || 10,
      };

      const response = await api.search.query(apiParams);
      const data = response.data;

      setResults(data.items);
      setPagination({
        page: data.page,
        page_size: data.page_size,
        total: data.total,
        total_pages: data.total_pages,
      });
    } catch (err) {
      console.error('Error searching:', err);
      setError(err.response?.data?.detail || 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []); // Remove searchParams dependency to prevent infinite loop

  const reset = () => {
    setSearchParams({
      q: '',
      theme_ids: [],
      source_types: [],
      page: 1,
      page_size: 10,
    });
    setResults([]);
    setError(null);
  };

  return {
    results,
    loading,
    error,
    pagination,
    searchParams,
    search,
    reset,
  };
};
