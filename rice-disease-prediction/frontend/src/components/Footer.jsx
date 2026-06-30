import { Link } from 'react-router-dom';
import { GiRiceCooker } from 'react-icons/gi';
import { HiHeart } from 'react-icons/hi';

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-surface-950/80 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                <GiRiceCooker className="text-white text-sm" />
              </div>
              <span className="font-display font-bold text-lg">
                <span className="text-white">Rice</span>
                <span className="text-primary-400">Guard</span>
                <span className="text-white/50 text-sm font-normal ml-1">AI</span>
              </span>
            </Link>
            <p className="text-white/40 text-sm max-w-md leading-relaxed">
              AI-powered rice leaf disease prediction system. Helping farmers identify and treat
              rice diseases quickly with deep learning technology.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4 uppercase tracking-wider">Quick Links</h4>
            <ul className="space-y-2">
              {[
                { path: '/', label: 'Home' },
                { path: '/predict', label: 'Predict Disease' },
                { path: '/history', label: 'Prediction History' },
              ].map((link) => (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    className="text-white/40 hover:text-primary-400 text-sm transition-colors duration-300"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4 uppercase tracking-wider">About</h4>
            <ul className="space-y-2 text-sm text-white/40">
              <li>Model: EfficientNet-B3</li>
              <li>Classes: 8 Disease Types</li>
              <li>Accuracy: &gt;90%</li>
              <li>API Docs: <a href="/docs" className="text-primary-400 hover:text-primary-300 transition-colors">/docs</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-white/5 mt-8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-white/30 text-xs">
            © {new Date().getFullYear()} RiceGuard AI. All rights reserved.
          </p>
          <p className="text-white/30 text-xs flex items-center gap-1">
            Made with <HiHeart className="text-red-400 text-sm" /> for farmers worldwide
          </p>
        </div>
      </div>
    </footer>
  );
}
