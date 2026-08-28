import React from 'react';
import { Target, Search, ShieldCheck, BarChart3, History, Settings, Cpu } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, systemInfo }) {
  const navItems = [
    { id: 'analyze', label: 'Analyze Conversation', icon: Search },
    { id: 'catalog', label: 'Facet Catalog', icon: Target },
    { id: 'safety', label: 'Safety & Abstention', icon: ShieldCheck },
    { id: 'benchmark', label: 'Benchmark Evaluation', icon: BarChart3 },
    { id: 'history', label: 'History Log', icon: History },
    { id: 'settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Logo Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)', marginBottom: '16px' }}>
        <div style={{ background: 'var(--accent-blue)', color: '#fff', padding: '6px', borderRadius: '8px', display: 'flex' }}>
          <Target size={20} />
        </div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)', lineHeight: 1.1 }}>FacetIQ</div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>AI Conversation Intelligence</div>
        </div>
      </div>

      {/* Navigation Options */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '9px 12px',
                borderRadius: '6px',
                border: 'none',
                background: isActive ? 'var(--accent-bg)' : 'transparent',
                color: isActive ? 'var(--accent-blue)' : 'var(--text-primary)',
                fontWeight: isActive ? 700 : 500,
                fontSize: '0.86rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease'
              }}
            >
              <Icon size={16} style={{ color: isActive ? 'var(--accent-blue)' : 'var(--text-muted)' }} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Active Infrastructure Metadata Footer */}
      <div style={{ paddingTop: '16px', borderTop: '1px solid var(--border-color)', marginTop: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
          <Cpu size={12} />
          <span>Active Infrastructure</span>
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div>Provider: <code style={{ background: 'var(--code-bg)', color: 'var(--code-text)', padding: '1px 5px', borderRadius: '4px', fontSize: '0.72rem' }}>{systemInfo?.model_provider?.toUpperCase() || 'LLM'}</code></div>
          <div>Model: <code style={{ background: 'var(--code-bg)', color: 'var(--code-text)', padding: '1px 5px', borderRadius: '4px', fontSize: '0.72rem' }}>{systemInfo?.model_name || 'GPT-4o'}</code></div>
          <div>Embeddings: <code style={{ background: 'var(--code-bg)', color: 'var(--code-text)', padding: '1px 5px', borderRadius: '4px', fontSize: '0.72rem' }}>{systemInfo?.embedding_model || 'all-MiniLM-L6-v2'}</code></div>
        </div>
      </div>
    </aside>
  );
}
