import React from 'react';
import { motion } from 'framer-motion';
import './Header.css';

function Header() {
  return (
    <motion.header 
      className="header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 21H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M5 21V7L12 3L19 7V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M9 21V15H15V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M9 10H9.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M15 10H15.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <span className="logo-text">RealTech</span>
        </div>

        <nav className="nav-links">
          <a href="#how-it-works" className="nav-link">How it Works</a>
          <a href="#about" className="nav-link">About</a>
        </nav>

        <div className="header-actions">
          <button className="btn btn-secondary">Sign In</button>
          <button className="btn btn-primary">Get Started</button>
        </div>

        <button className="mobile-menu-btn">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>
    </motion.header>
  );
}

export default Header;
