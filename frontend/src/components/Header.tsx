'use client';

import { Home, TrendingUp } from 'lucide-react';

export default function Header() {
  return (
    <header className="w-full py-4 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <nav className="glass-card rounded-2xl px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-dark-cyan to-emerald-500 flex items-center justify-center">
              <Home className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">RealTech</span>
          </div>

          {/* Navigation Links */}
          <div className="hidden sm:flex items-center space-x-8">
            <a href="#" className="text-gray-600 hover:text-dark-cyan transition-colors font-medium">
              Home
            </a>
            <a href="#" className="text-gray-600 hover:text-dark-cyan transition-colors font-medium">
              About
            </a>
            <a href="#" className="text-gray-600 hover:text-dark-cyan transition-colors font-medium">
              API
            </a>
          </div>

          {/* CTA Button */}
          <button className="btn-primary px-5 py-2.5 rounded-xl text-white font-medium flex items-center space-x-2">
            <TrendingUp className="w-4 h-4" />
            <span>Get Started</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
