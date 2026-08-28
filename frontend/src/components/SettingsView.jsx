import React from 'react';
import { Settings, Cpu, Shield, Server } from 'lucide-react';

export default function SettingsView({ systemInfo }) {
  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <h2>System Settings & Configuration</h2>
        <p className="subtitle">Infrastructure configuration and active model provider settings.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Cpu size={18} style={{ color: 'var(--accent-blue)' }} />
            <span>AI Model & Embedding Provider</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.88rem' }}>
            <div>
              <label style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.78rem', fontWeight: 600 }}>MODEL PROVIDER</label>
              <code style={{ background: 'var(--code-bg)', color: 'var(--code-text)', padding: '4px 8px', borderRadius: '4px' }}>{systemInfo?.model_provider || 'Groq / Gemini'}</code>
            </div>

            <div>
              <label style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.78rem', fontWeight: 600 }}>MODEL NAME</label>
              <code style={{ background: 'var(--code-bg)', color: 'var(--code-text)', padding: '4px 8px', borderRadius: '4px' }}>{systemInfo?.model_name || 'llama-3.3-70b-versatile'}</code>
            </div>

            <div>
              <label style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.78rem', fontWeight: 600 }}>VECTOR EMBEDDING MODEL</label>
              <code style={{ background: 'var(--code-bg)', color: 'var(--code-text)', padding: '4px 8px', borderRadius: '4px' }}>{systemInfo?.embedding_model || 'all-MiniLM-L6-v2'}</code>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Server size={18} style={{ color: 'var(--accent-blue)' }} />
            <span>Retrieval & Pipeline Tuning</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.88rem' }}>
            <div>
              <label style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.78rem', fontWeight: 600 }}>TOP-K CANDIDATE RETRIEVAL</label>
              <input type="number" defaultValue={systemInfo?.top_k_retrieval || 10} className="input-text" style={{ width: '100%', marginTop: '4px' }} readOnly />
            </div>

            <div>
              <label style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.78rem', fontWeight: 600 }}>SCORING BATCH SIZE</label>
              <input type="number" defaultValue={systemInfo?.scoring_batch_size || 5} className="input-text" style={{ width: '100%', marginTop: '4px' }} readOnly />
            </div>

            <div>
              <label style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.78rem', fontWeight: 600 }}>ENVIRONMENT</label>
              <span className="badge badge-scored">Enterprise Production</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
