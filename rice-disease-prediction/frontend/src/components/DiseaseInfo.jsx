import { motion } from 'framer-motion';
import { HiX, HiShieldCheck, HiBeaker, HiLightBulb } from 'react-icons/hi';
import { getSeverityColor, getSeverityLabel } from '../utils/formatters';

export default function DiseaseInfo({ disease, onClose }) {
  if (!disease) return null;
  const sev = getSeverityColor(disease.severity);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      onClick={onClose}>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', damping: 25 }}
        className="glass-strong rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto p-6"
        onClick={(e) => e.stopPropagation()}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-display font-bold text-white">{disease.name}</h2>
            <span className={`inline-block mt-1 px-2.5 py-1 rounded-md text-xs font-semibold ${sev.bg} ${sev.text}`}>
              {getSeverityLabel(disease.severity)}
            </span>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
            <HiX className="text-lg" />
          </button>
        </div>
        <p className="text-white/50 text-sm leading-relaxed mb-4">{disease.description}</p>
        {disease.symptoms?.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-white/60 mb-2">Symptoms</h3>
            <ul className="space-y-1">
              {disease.symptoms.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-white/50">
                  <span className="text-primary-400 mt-0.5">•</span>{s}
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="space-y-3">
          {[{ icon: <HiBeaker />, label: 'Chemical Treatment', text: disease.treatment?.chemical },
            { icon: <HiShieldCheck />, label: 'Organic Treatment', text: disease.treatment?.organic },
            { icon: <HiLightBulb />, label: 'Prevention', text: disease.treatment?.prevention }
          ].map((item) => (
            <div key={item.label} className="p-3 rounded-xl bg-white/3 border border-white/5">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-primary-400">{item.icon}</span>
                <span className="text-xs font-semibold text-white/60">{item.label}</span>
              </div>
              <p className="text-xs text-white/50 leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
