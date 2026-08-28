import React, { useState, useEffect } from 'react';
import { Target, Search, Filter } from 'lucide-react';

export default function CatalogView() {
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/catalog')
      .then(res => res.json())
      .then(data => {
        setCatalog(data.facets || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Catalog fetch error:', err);
        setLoading(false);
      });
  }, []);

  const types = ['All', ...new Set(catalog.map(f => f.facet_type).filter(Boolean))];
  const observableCount = catalog.filter(f => f.conversation_observable === true || String(f.conversation_observable).toLowerCase() === 'true').length;

  let filtered = catalog.filter(item => {
    const matchesSearch = !search.trim() || (item.facet_normalized || '').toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'All' || item.facet_type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <h2>Facet Catalog</h2>
        <p className="subtitle">Browse and understand the available evaluation facets.</p>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div className="summary-card">
          <div className="summary-value">{catalog.length}</div>
          <div className="summary-label">Total Facets</div>
        </div>
        <div className="summary-card">
          <div className="summary-value" style={{ color: 'var(--scored-color)' }}>{observableCount}</div>
          <div className="summary-label">Observable</div>
        </div>
        <div className="summary-card">
          <div className="summary-value" style={{ color: 'var(--unobs-color)' }}>{catalog.length - observableCount}</div>
          <div className="summary-label">Not Observable</div>
        </div>
      </div>

      {/* Filter Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginBottom: '20px' }}>
        <div style={{ position: 'relative' }}>
          <Search size={15} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search facets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-text"
            style={{ paddingLeft: '32px', width: '100%' }}
          />
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="input-select"
        >
          {types.map(t => (
            <option key={t} value={t}>{t === 'All' ? 'Filter by Type: All' : t}</option>
          ))}
        </select>
      </div>

      {/* Catalog Table */}
      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>Loading catalog...</div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Facet Name</th>
                <th>Type</th>
                <th>Observable</th>
                <th>Sensitivity</th>
                <th>Definition</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 700 }}>{item.facet_normalized}</td>
                  <td><span className="badge" style={{ background: 'var(--code-bg)', color: 'var(--code-text)' }}>{item.facet_type || 'General'}</span></td>
                  <td>
                    {item.conversation_observable ? (
                      <span className="badge badge-scored">Yes</span>
                    ) : (
                      <span className="badge badge-unobs">No</span>
                    )}
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>{item.sensitivity || 'Normal'}</td>
                  <td style={{ color: 'var(--text-secondary)', maxWidth: '400px' }}>{item.scoring_definition || item.definition || 'Standard evaluation criterion.'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
