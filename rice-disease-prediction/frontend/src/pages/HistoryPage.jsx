import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import HistoryTable from '../components/HistoryTable';
import DiseaseInfo from '../components/DiseaseInfo';
import { historyAPI } from '../api/client';

const COLORS = ['#22c55e','#ef4444','#f59e0b','#3b82f6','#a855f7','#ec4899','#14b8a6','#f97316'];

export default function HistoryPage() {
  const [predictions, setPredictions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [selectedPred, setSelectedPred] = useState(null);
  const perPage = 10;

  const fetchHistory = async (p = 1) => {
    setLoading(true);
    try {
      const res = await historyAPI.getHistory({ page: p, per_page: perPage });
      setPredictions(res.data.data);
      setTotal(res.data.total);
      setPage(p);
    } catch { toast.error('Failed to load history'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchHistory(); }, []);

  const handleDelete = async (id) => {
    if (!confirm('Delete this prediction?')) return;
    try {
      await historyAPI.delete(id);
      toast.success('Prediction deleted');
      fetchHistory(page);
    } catch { toast.error('Delete failed'); }
  };

  const handleView = async (id) => {
    try {
      const res = await historyAPI.getDetail(id);
      setSelectedPred(res.data.data);
    } catch { toast.error('Failed to load details'); }
  };

  // Chart data
  const diseaseDistribution = predictions.reduce((acc, p) => {
    const existing = acc.find(d => d.name === p.disease_name);
    if (existing) existing.value++;
    else acc.push({ name: p.disease_name, value: 1 });
    return acc;
  }, []);

  const confidenceData = predictions.slice(0, 8).map(p => ({
    name: p.disease_name.substring(0, 10),
    confidence: Math.round(p.confidence * 100),
  }));

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-display font-bold text-white mb-2">Prediction History</h1>
          <p className="text-white/40">View and manage your past disease predictions.</p>
        </motion.div>

        {/* Charts */}
        {predictions.length > 0 && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
              <h3 className="text-sm font-semibold text-white/60 mb-4 uppercase tracking-wider">Disease Distribution</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={diseaseDistribution} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
                    paddingAngle={3} dataKey="value" stroke="none">
                    {diseaseDistribution.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#262626', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-wrap gap-2 mt-2">
                {diseaseDistribution.map((d, i) => (
                  <span key={d.name} className="flex items-center gap-1.5 text-xs text-white/50">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                    {d.name}
                  </span>
                ))}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
              <h3 className="text-sm font-semibold text-white/60 mb-4 uppercase tracking-wider">Recent Confidence Scores</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={confidenceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.4)' }} />
                  <YAxis tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.4)' }} domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: '#262626', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                  <Bar dataKey="confidence" fill="#22c55e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          </div>
        )}

        {/* Table */}
        {loading ? (
          <div className="card space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-14 bg-white/5 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <HistoryTable predictions={predictions} total={total} page={page} perPage={perPage}
            onPageChange={fetchHistory} onView={handleView} onDelete={handleDelete} />
        )}
      </div>

      {/* Detail Modal */}
      {selectedPred && (
        <DiseaseInfo disease={{
          name: selectedPred.disease_name,
          severity: selectedPred.severity,
          description: '',
          symptoms: [],
          treatment: selectedPred.treatment,
        }} onClose={() => setSelectedPred(null)} />
      )}
    </div>
  );
}
