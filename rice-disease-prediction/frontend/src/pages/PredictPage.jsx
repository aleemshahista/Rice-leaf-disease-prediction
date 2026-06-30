import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import ImageUploader from '../components/ImageUploader';
import PredictionCard from '../components/PredictionCard';
import GradCamView from '../components/GradCamView';
import { usePrediction } from '../hooks/usePrediction';

export default function PredictPage() {
  const [file, setFile] = useState(null);
  const { result, loading, error, predict, reset } = usePrediction();

  const handleFileSelect = useCallback((selectedFile) => {
    setFile(selectedFile);
    if (!selectedFile) reset();
  }, [reset]);

  const handleAnalyze = async () => {
    if (!file) { toast.error('Please select an image first'); return; }
    try {
      await predict(file);
      toast.success('Analysis complete!');
    } catch {
      toast.error(error || 'Analysis failed');
    }
  };

  const handleReset = () => {
    setFile(null);
    reset();
  };

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-display font-bold text-white mb-2">Disease Prediction</h1>
          <p className="text-white/40 max-w-lg mx-auto">Upload a rice leaf image to get instant AI-powered disease diagnosis.</p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left: Upload */}
          <div className="space-y-6">
            <ImageUploader onFileSelect={handleFileSelect} disabled={loading} />
            <div className="flex gap-3">
              <button onClick={handleAnalyze} disabled={!file || loading} className="btn-primary flex-1 gap-2">
                {loading ? (
                  <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Analyzing...</>
                ) : 'Analyze Image'}
              </button>
              {(file || result) && (
                <button onClick={handleReset} className="btn-secondary px-4">Reset</button>
              )}
            </div>
            {/* Loading skeleton */}
            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card space-y-4">
                <div className="h-6 w-48 bg-white/5 rounded-lg animate-pulse" />
                <div className="h-4 w-full bg-white/5 rounded animate-pulse" />
                <div className="h-3 w-3/4 bg-white/5 rounded animate-pulse" />
                <div className="h-20 w-full bg-white/5 rounded-xl animate-pulse" />
                <div className="h-4 w-1/2 bg-white/5 rounded animate-pulse" />
              </motion.div>
            )}
          </div>

          {/* Right: Results */}
          <div className="space-y-6">
            {result && <PredictionCard result={result} />}
            {result && <GradCamView originalUrl={result.image_url} gradcamUrl={result.gradcam_url} />}
            {!result && !loading && (
              <div className="card flex flex-col items-center justify-center py-20 text-center">
                <div className="text-5xl mb-4 opacity-20">🔬</div>
                <h3 className="text-white/30 font-semibold mb-1">Results will appear here</h3>
                <p className="text-white/20 text-sm">Upload an image and click Analyze to begin.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
