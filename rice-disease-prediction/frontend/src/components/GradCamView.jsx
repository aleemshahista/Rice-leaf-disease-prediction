import { useState } from 'react';
import { motion } from 'framer-motion';
import { HiEye, HiEyeOff } from 'react-icons/hi';

export default function GradCamView({ originalUrl, gradcamUrl }) {
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [opacity, setOpacity] = useState(0.6);

  if (!gradcamUrl) return null;

  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
          Grad-CAM Visualization
        </h3>
        <button onClick={() => setShowHeatmap(!showHeatmap)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-white/5 text-white/50 hover:text-white hover:bg-white/10 transition-all">
          {showHeatmap ? <HiEyeOff /> : <HiEye />}
          {showHeatmap ? 'Hide' : 'Show'} Heatmap
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="rounded-xl overflow-hidden bg-black/20 border border-white/5">
          <div className="px-3 py-2 border-b border-white/5">
            <span className="text-xs text-white/40 font-medium">Original Image</span>
          </div>
          <div className="p-2">
            <img src={`${baseUrl}${originalUrl}`} alt="Original rice leaf"
              className="w-full h-48 object-contain rounded-lg" />
          </div>
        </div>

        <div className="rounded-xl overflow-hidden bg-black/20 border border-white/5">
          <div className="px-3 py-2 border-b border-white/5">
            <span className="text-xs text-white/40 font-medium">Grad-CAM Heatmap</span>
          </div>
          <div className="p-2">
            <img
              src={`${baseUrl}${showHeatmap ? gradcamUrl : originalUrl}`}
              alt="Grad-CAM heatmap"
              className="w-full h-48 object-contain rounded-lg"
              style={{ opacity: showHeatmap ? opacity : 1 }}
            />
          </div>
        </div>
      </div>

      {showHeatmap && (
        <div className="mt-4 flex items-center gap-3">
          <span className="text-xs text-white/40 w-16">Opacity</span>
          <input type="range" min="0.1" max="1" step="0.05" value={opacity}
            onChange={(e) => setOpacity(parseFloat(e.target.value))}
            className="flex-1 h-1.5 rounded-full bg-white/10 appearance-none cursor-pointer
              [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
              [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-500 [&::-webkit-slider-thumb]:cursor-pointer" />
          <span className="text-xs text-white/40 w-10 text-right">{Math.round(opacity * 100)}%</span>
        </div>
      )}

      <p className="mt-3 text-xs text-white/30 italic">
        Warmer colors (red/yellow) indicate regions the model focused on most for its prediction.
      </p>
    </motion.div>
  );
}
