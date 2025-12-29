import { useState, useEffect } from 'react';
import api from '../services/api';

export const useThemes = () => {
  const [themes, setThemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchThemes = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.themes.getAll();
      setThemes(response.data);
    } catch (err) {
      console.error('Error fetching themes:', err);
      setError(err.response?.data?.detail || 'Failed to load themes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchThemes();
  }, []);

  const refetch = () => {
    fetchThemes();
  };

  return {
    themes,
    loading,
    error,
    refetch,
  };
};
