import { useState } from 'react';
import { motion } from 'framer-motion';
import { HiChevronDown, HiShieldCheck, HiBeaker, HiLightBulb } from 'react-icons/hi';
import { formatConfidence, getSeverityColor, getSeverityLabel } from '../utils/formatters';

export default function PredictionCard({ result }) {
  const [openTab, setOpenTab] = useState('chemical');

  if (!result) return null;

  const severity = getSeverityColor(result.severity);

  const treatmentTabs = [
    { key: 'chemical', label: 'Chemical', icon: <HiBeaker />, content: result.treatment?.chemical },
    { key: 'organic', label: 'Organic', icon: <HiShieldCheck />, content: result.treatment?.organic },
    { key: 'prevention', label: 'Prevention', icon: <HiLightBulb />, content: result.treatment?.prevention },
  ];

  // Top 5 probabilities
  const topProbs = (result.all_probabilities || []).slice(0, 5);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="card space-y-6"
    >
      {/* Header: Disease Name + Severity */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-display font-bold text-white mb-1">
            {result.disease_name}
          </h2>
          {result.description && (
            <p className="text-white/50 text-sm leading-relaxed max-w-lg">
              {result.description}
            </p>
          )}
        </div>
        <span className={`shrink-0 px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider ${severity.bg} ${severity.text} ${severity.border} border`}>
          {getSeverityLabel(result.severity)}
        </span>
      </div>

      {/* Confidence */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-white/50">Confidence</span>
          <span className="text-lg font-bold text-primary-400">
            {formatConfidence(result.confidence)}
          </span>
        </div>
        <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${result.confidence * 100}%` }}
            transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
            className="h-full rounded-full bg-gradient-to-r from-primary-600 to-primary-400"
          />
        </div>
      </div>

      {/* Top Probabilities */}
      <div>
        <h3 className="text-sm font-semibold text-white/60 mb-3 uppercase tracking-wider">
          All Predictions
        </h3>
        <div className="space-y-2">
          {topProbs.map((prob, i) => (
            <div key={prob.class_name} className="flex items-center gap-3">
              <span className="text-xs text-white/40 w-36 truncate">{prob.class_name}</span>
              <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${prob.probability * 100}%` }}
                  transition={{ duration: 0.8, delay: 0.4 + i * 0.1 }}
                  className={`h-full rounded-full ${
                    i === 0 ? 'bg-primary-500' : 'bg-white/20'
                  }`}
                />
              </div>
              <span className="text-xs text-white/40 w-14 text-right">
                {(prob.probability * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Symptoms */}
      {result.symptoms && result.symptoms.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-white/60 mb-3 uppercase tracking-wider">
            Symptoms
          </h3>
          <ul className="space-y-1.5">
            {result.symptoms.map((symptom, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-white/50">
                <span className="text-primary-400 mt-1">•</span>
                {symptom}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Treatment Tabs */}
      <div>
        <h3 className="text-sm font-semibold text-white/60 mb-3 uppercase tracking-wider">
          Treatment Recommendations
        </h3>

        {/* Tab buttons */}
        <div className="flex gap-1 p-1 rounded-xl bg-white/5 mb-4">
          {treatmentTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setOpenTab(tab.key)}
              className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-300 ${
                openTab === tab.key
                  ? 'bg-primary-500/20 text-primary-400'
                  : 'text-white/40 hover:text-white/60'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <motion.div
          key={openTab}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="p-4 rounded-xl bg-white/3 border border-white/5"
        >
          <p className="text-sm text-white/60 leading-relaxed">
            {treatmentTabs.find((t) => t.key === openTab)?.content || 'No treatment information available.'}
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
