import { motion } from 'framer-motion';
import { HiTrash, HiEye, HiChevronLeft, HiChevronRight } from 'react-icons/hi';
import { formatDate, formatConfidence, getSeverityColor } from '../utils/formatters';

export default function HistoryTable({ predictions, total, page, perPage, onPageChange, onView, onDelete }) {
  const totalPages = Math.ceil(total / perPage);
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';

  if (!predictions || predictions.length === 0) {
    return (
      <div className="card text-center py-16">
        <div className="text-4xl mb-3">🌾</div>
        <h3 className="text-white font-semibold mb-1">No predictions yet</h3>
        <p className="text-white/40 text-sm">Upload a rice leaf image to get your first prediction.</p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden !p-0">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5">
              {['Image', 'Disease', 'Confidence', 'Severity', 'Date', 'Actions'].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-white/40 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {predictions.map((pred, i) => {
              const sev = getSeverityColor(pred.severity);
              return (
                <motion.tr key={pred.prediction_id}
                  initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="hover:bg-white/3 transition-colors">
                  <td className="px-4 py-3">
                    <img src={`${baseUrl}${pred.image_url}`} alt="" className="w-12 h-12 rounded-lg object-cover bg-white/5" />
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-white">{pred.disease_name}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 rounded-full bg-white/10 overflow-hidden">
                        <div className="h-full bg-primary-500 rounded-full" style={{ width: `${pred.confidence * 100}%` }} />
                      </div>
                      <span className="text-xs text-white/50">{formatConfidence(pred.confidence)}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${sev.bg} ${sev.text}`}>
                      {pred.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-white/40">{formatDate(pred.timestamp)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => onView && onView(pred.prediction_id)}
                        className="p-1.5 rounded-lg text-white/40 hover:text-primary-400 hover:bg-primary-500/10 transition-colors">
                        <HiEye className="text-sm" />
                      </button>
                      <button onClick={() => onDelete && onDelete(pred.prediction_id)}
                        className="p-1.5 rounded-lg text-white/40 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                        <HiTrash className="text-sm" />
                      </button>
                    </div>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-white/5">
          <span className="text-xs text-white/40">Page {page} of {totalPages} ({total} total)</span>
          <div className="flex items-center gap-1">
            <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
              className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
              <HiChevronLeft />
            </button>
            <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}
              className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
              <HiChevronRight />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
