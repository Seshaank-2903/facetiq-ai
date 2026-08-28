import React from 'react';
import { History, Play } from 'lucide-react';

export default function HistoryView({ history, onLoadHistoryItem }) {
  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <h2>History Log</h2>
        <p className="subtitle">View past conversation evaluation sessions.</p>
      </div>

      {history.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          No past evaluation history available in this session.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {history.map((item, idx) => (
            <div key={idx} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  {item.timestamp}
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  "{item.snippet}"
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Candidates: {item.result.retrieved_candidates_count} • Latency: {item.result.latency_sec}s
                </div>
              </div>

              <button className="btn-secondary" onClick={() => onLoadHistoryItem(item)}>
                <span>Load Session</span>
                <Play size={13} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
