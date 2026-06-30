import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiArrowRight, HiCloudUpload, HiChartBar, HiShieldCheck } from 'react-icons/hi';
import { GiRiceCooker, GiMicroscope, GiMedicines } from 'react-icons/gi';

const fadeUp = { hidden: { opacity: 0, y: 30 }, visible: (i = 0) => ({ opacity: 1, y: 0, transition: { delay: i * 0.15, duration: 0.6 } }) };

export default function HomePage() {
  const stats = [
    { value: '8', label: 'Disease Classes', icon: '🦠' },
    { value: '>90%', label: 'Model Accuracy', icon: '🎯' },
    { value: '<3s', label: 'Prediction Time', icon: '⚡' },
    { value: '24/7', label: 'Available', icon: '🌐' },
  ];

  const steps = [
    { icon: <HiCloudUpload className="text-2xl" />, title: 'Upload Image', desc: 'Take a photo of the rice leaf or upload an existing image.' },
    { icon: <GiMicroscope className="text-2xl" />, title: 'AI Analysis', desc: 'Our EfficientNet-B3 model analyzes the leaf in seconds.' },
    { icon: <GiMedicines className="text-2xl" />, title: 'Get Treatment', desc: 'Receive disease diagnosis with treatment recommendations.' },
  ];

  const diseases = ['Blast', 'Brown Spot', 'Sheath Blight', 'Bacterial Leaf Blight', 'Tungro', 'False Smut', 'Narrow Brown Leaf Spot', 'Healthy'];

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-950 via-surface-950 to-surface-950" />
        <div className="absolute inset-0 bg-grid opacity-50" />
        <div className="absolute top-20 -left-32 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 -right-32 w-96 h-96 bg-accent-500/8 rounded-full blur-3xl" />

        <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
          <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={0}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm mb-6">
            <GiRiceCooker /> AI-Powered Disease Detection
          </motion.div>

          <motion.h1 variants={fadeUp} custom={1} initial="hidden" animate="visible"
            className="text-5xl sm:text-6xl lg:text-7xl font-display font-extrabold mb-6 leading-tight">
            Protect Your{' '}
            <span className="gradient-text">Rice Crops</span>
            <br />with AI Precision
          </motion.h1>

          <motion.p variants={fadeUp} custom={2} initial="hidden" animate="visible"
            className="text-lg sm:text-xl text-white/50 max-w-2xl mx-auto mb-8 leading-relaxed">
            Upload a rice leaf image and get instant disease diagnosis with treatment
            recommendations powered by deep learning.
          </motion.p>

          <motion.div variants={fadeUp} custom={3} initial="hidden" animate="visible"
            className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/predict" className="btn-primary text-base px-8 py-4 gap-2">
              Start Diagnosis <HiArrowRight />
            </Link>
            <a href="#how-it-works" className="btn-secondary text-base px-8 py-4">
              How It Works
            </a>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 border-y border-white/5">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, i) => (
              <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}
                className="text-center p-6 rounded-2xl bg-white/3 border border-white/5 hover:border-primary-500/20 transition-colors">
                <div className="text-2xl mb-2">{stat.icon}</div>
                <div className="text-3xl font-display font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-white/40">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-3">How It Works</h2>
            <p className="text-white/40 max-w-xl mx-auto">Three simple steps to diagnose rice leaf diseases.</p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <motion.div key={step.title} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                className="relative card text-center group hover:border-primary-500/20 transition-all">
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-primary-500 text-white text-sm font-bold flex items-center justify-center shadow-glow">
                  {i + 1}
                </div>
                <div className="w-14 h-14 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mx-auto mb-4 text-primary-400 group-hover:shadow-glow transition-shadow">
                  {step.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-white/40 leading-relaxed">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Diseases we detect */}
      <section className="py-20 border-t border-white/5">
        <div className="max-w-6xl mx-auto px-4">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-3">Diseases We Detect</h2>
            <p className="text-white/40 max-w-xl mx-auto">Our model can identify 7 common rice diseases plus healthy leaves.</p>
          </motion.div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {diseases.map((name, i) => (
              <motion.div key={name} initial={{ opacity: 0, scale: 0.9 }} whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }} transition={{ delay: i * 0.05 }}
                className="p-4 rounded-xl bg-white/3 border border-white/5 text-center hover:border-primary-500/30 hover:bg-primary-500/5 transition-all cursor-default">
                <div className="text-2xl mb-2">{name === 'Healthy' ? '✅' : '🍂'}</div>
                <span className="text-sm font-medium text-white/70">{name}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-900/50 via-primary-800/30 to-surface-900 border border-primary-500/20 p-10 sm:p-14 text-center">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/10 rounded-full blur-3xl" />
            <h2 className="relative text-3xl sm:text-4xl font-display font-bold text-white mb-4">Ready to Protect Your Crops?</h2>
            <p className="relative text-white/50 mb-8 max-w-lg mx-auto">Start using AI-powered disease detection today. Free to use and available 24/7.</p>
            <Link to="/register" className="relative btn-primary text-base px-8 py-4 gap-2">
              Get Started Free <HiArrowRight />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
