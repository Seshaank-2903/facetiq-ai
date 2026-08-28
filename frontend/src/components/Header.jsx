import React from 'react';
import { Target, ExternalLink } from 'lucide-react';

export default function Header({ theme, toggleTheme, apiStatus }) {
  const isDark = theme === 'dark';
  const toggleText = isDark ? 'Light' : 'Dark';

  return (
    <header className="header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <h2 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 800 }}>FacetIQ</h2>
          <span className="badge" style={{ background: 'var(--accent-bg)', color: 'var(--accent-blue)', border: '1px solid var(--border-color)', fontSize: '0.7rem' }}>
            ENTERPRISE
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-secondary)', background: 'var(--border-muted)', padding: '2px 8px', borderRadius: '4px' }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: apiStatus ? '#22c55e' : '#ef4444' }}></span>
          {apiStatus ? 'API Connected' : 'API Offline'}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button
          onClick={toggleTheme}
          className="deploy-theme-toggle"
          title="Toggle Dark / Light Theme"
        >
          {toggleText}
        </button>

        <button
          className="btn-primary"
          style={{ fontSize: '0.8rem', padding: '5px 14px', minHeight: '30px' }}
          onClick={() => alert('FacetIQ Enterprise deployed to production cluster.')}
        >
          <span>Deploy</span>
          <ExternalLink size={13} />
        </button>
      </div>
    </header>
  );
}
