import { useState } from 'react';
import { predictionAPI } from '../api/client';

export function usePrediction() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const predict = async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await predictionAPI.predict(formData);
      setResult(response.data.data);
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Prediction failed. Please try again.';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    setLoading(false);
  };

  return { result, loading, error, predict, reset };
}
