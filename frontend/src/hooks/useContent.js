import { useState, useEffect } from 'react';
import api from '../services/api';

export const useContent = (filters = {}) => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 0,
  });

  const fetchContent = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        page: 1,
        page_size: 10,
        ...filters,
      };

      const response = await api.content.getAll(params);
      const data = response.data;

      setContent(data.items);
      setPagination({
        page: data.page,
        page_size: data.page_size,
        total: data.total,
        total_pages: data.total_pages,
      });
    } catch (err) {
      console.error('Error fetching content:', err);
      setError(err.response?.data?.detail || 'Failed to load content');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only fetch on mount

  const refetch = () => {
    fetchContent();
  };

  return {
    content,
    loading,
    error,
    pagination,
    refetch,
  };
};

export const useContentDetail = (contentId) => {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!contentId) return;

    const fetchContent = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await api.content.getById(contentId);
        setContent(response.data);
      } catch (err) {
        console.error('Error fetching content detail:', err);
        setError(err.response?.data?.detail || 'Failed to load content');
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [contentId]);

  return { content, loading, error };
};
