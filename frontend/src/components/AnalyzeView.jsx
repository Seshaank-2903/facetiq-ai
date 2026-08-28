import React, { useState } from 'react';
import { Play, Upload, Shield, Download, Search, X, CheckCircle, AlertCircle, FileText, ChevronRight } from 'lucide-react';

const PRESET_SCENARIOS = {
  "Custom Input": "",
  "Scenario 1: Executive Presentation (High Confidence)": "I gave a presentation yesterday to the executive board and answered all questions calmly and confidently.",
  "Scenario 2: Sarcasm & Panic Trap": "I absolutely LOVE presenting to 500 people... my heart was racing and I felt like I was going to throw up.",
  "Scenario 3: Medical Measurement Trap": "I've been feeling dizzy lately when I wake up. My doctor checked my blood pressure yesterday.",
  "Scenario 4: Third-Person Manager Quote Trap": "My manager told me yesterday that I handled the client presentation effectively and demonstrated strong leadership.",
  "Scenario 5: Code-Switching Fluency": "Presentation start hone ke baad I became very comfortable and explained the entire architecture smoothly."
};

export default function AnalyzeView({ currentAnalysis, onRunAnalysis, history, isAnalyzing }) {
  const [inputText, setInputText] = useState(
    currentAnalysis?.conversation || "I gave a presentation yesterday to the executive board and answered all questions calmly and confidently."
  );
  const [selectedPreset, setSelectedPreset] = useState("Scenario 1: Executive Presentation (High Confidence)");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [sortBy, setSortBy] = useState("Default Order");
  const [selectedDetail, setSelectedDetail] = useState(null);

  const handlePresetChange = (e) => {
    const key = e.target.value;
    setSelectedPreset(key);
    if (key !== "Custom Input" && PRESET_SCENARIOS[key]) {
      setInputText(PRESET_SCENARIOS[key]);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setInputText(event.target.result);
        setSelectedPreset("Custom Input");
      };
      reader.readAsText(file);
    }
  };

  const handleAnalyzeClick = () => {
    if (!inputText.trim() || isAnalyzing) return;
    onRunAnalysis(inputText);
  };

  const charCount = inputText.trim().length;

  // Filter & Sort facet results
  const resList = currentAnalysis?.results || [];
  const scoredCount = resList.filter(r => r.status === 'scored').length;
  const abstainedCount = resList.filter(r => r.status !== 'scored').length;
  
  const confidences = resList.filter(r => r.status === 'scored').map(r => r.confidence);
  const avgConf = confidences.length ? (confidences.reduce((a, b) => a + b, 0) / confidences.length) : 0;

  let filteredResults = [...resList];
  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase().trim();
    filteredResults = filteredResults.filter(r => r.facet.toLowerCase().includes(q));
  }

  if (statusFilter === 'Scored') {
    filteredResults = filteredResults.filter(r => r.status === 'scored');
  } else if (statusFilter === 'Abstained') {
    filteredResults = filteredResults.filter(r => r.status !== 'scored');
  }

  if (sortBy === 'Score') {
    filteredResults.sort((a, b) => ((b.score ?? -1) - (a.score ?? -1)));
  } else if (sortBy === 'Confidence') {
    filteredResults.sort((a, b) => b.confidence - a.confidence);
  } else if (sortBy === 'Facet Name') {
    filteredResults.sort((a, b) => a.facet.localeCompare(b.facet));
  }

  const renderScoreDots = (score) => {
    if (!score || score < 1) return null;
    return (
      <div className="score-dots-wrapper">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className={`score-dot ${i <= score ? 'score-dot-active' : ''}`} />
        ))}
      </div>
    );
  };

  const getScoreLabel = (score) => {
    const labels = {
      1: "Very Weak Evidence",
      2: "Weak Evidence",
      3: "Moderate Evidence",
      4: "Strong Evidence",
      5: "Very Strong Evidence"
    };
    return labels[score] || "Unscored";
  };

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(currentAnalysis, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `facetiq_analysis_${Date.now()}.json`;
    a.click();
  };

  const exportCSV = () => {
    if (!resList.length) return;
    const headers = ["facet", "status", "score", "confidence", "evidence", "reason"];
    const rows = resList.map(r => [
      `"${r.facet}"`,
      `"${r.status}"`,
      r.score ?? "Null",
      r.confidence,
      `"${(r.evidence || "").replace(/"/g, '""')}"`,
      `"${(r.reason || "").replace(/"/g, '""')}"`
    ]);
    const csvContent = [headers.join(","), ...rows.map(row => row.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `facetiq_analysis_${Date.now()}.csv`;
    a.click();
  };

  return (
    <div>
      {/* Header Title Section */}
      <div style={{ marginBottom: '20px' }}>
        <h2>Conversation Analysis</h2>
        <p className="subtitle">Evaluate conversational evidence against relevant facets.</p>
      </div>

      {/* Preset & File Upload Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <div>
          <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
            Load Sample Conversation:
          </label>
          <select
            value={selectedPreset}
            onChange={handlePresetChange}
            className="input-select"
            style={{ width: '100%' }}
          >
            {Object.keys(PRESET_SCENARIOS).map((key) => (
              <option key={key} value={key}>{key}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
            Upload Text File (.txt):
          </label>
          <label className="btn-secondary" style={{ width: '100%', justifyContent: 'center', cursor: 'pointer' }}>
            <Upload size={14} />
            <span>Upload File</span>
            <input type="file" accept=".txt" onChange={handleFileUpload} style={{ display: 'none' }} />
          </label>
        </div>
      </div>

      {/* Conversation Text Area */}
      <div style={{ marginBottom: '16px' }}>
        <textarea
          className="input-textarea"
          rows={4}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste a conversation here..."
        />
        <div style={{ textAlign: 'right', fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Character Count: <strong style={{ color: 'var(--text-primary)' }}>{charCount}</strong>
        </div>
      </div>

      {/* Action Button & Hint */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '28px' }}>
        <button
          className="btn-primary"
          onClick={handleAnalyzeClick}
          disabled={charCount === 0 || isAnalyzing}
          style={{ minWidth: '180px', justifyContent: 'center' }}
        >
          {isAnalyzing ? (
            <>
              <div style={{ width: 14, height: 14, border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%' }} className="animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Play size={15} fill="currentColor" />
              <span>Analyze Conversation</span>
            </>
          )}
        </button>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          The system evaluates only evidence supported by the conversation.
        </span>
      </div>

      {/* Execution Animated Step Loader */}
      {isAnalyzing && (
        <div className="card" style={{ marginBottom: '24px', borderLeft: '4px solid var(--accent-blue)' }}>
          <h4 style={{ color: 'var(--accent-blue)', marginBottom: '8px' }}>Analyzing Conversation Pipeline</h4>
          <div style={{ fontSize: '0.84rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div>✓ Reading conversation context</div>
            <div>✓ Retrieving candidate facets from vector catalog</div>
            <div style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>● Evaluating evidence & applying safety filters...</div>
            <div style={{ color: 'var(--text-muted)' }}>○ Validating batch scores</div>
          </div>
        </div>
      )}

      {/* Results Workspace */}
      {currentAnalysis && !isAnalyzing && (
        <div>
          <div style={{ marginBottom: '16px' }}>
            <h3>Analysis Results</h3>
            <p className="subtitle">Evidence-based facet evaluation</p>
          </div>

          {/* Metric Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '20px' }}>
            <div className="summary-card">
              <div className="summary-value">{currentAnalysis.retrieved_candidates_count}</div>
              <div className="summary-label">Retrieved</div>
            </div>
            <div className="summary-card">
              <div className="summary-value" style={{ color: 'var(--scored-color)' }}>{scoredCount}</div>
              <div className="summary-label">Scored</div>
            </div>
            <div className="summary-card">
              <div className="summary-value" style={{ color: 'var(--abstain-color)' }}>{abstainedCount}</div>
              <div className="summary-label">Abstained</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{(avgConf * 100).toFixed(0)}%</div>
              <div className="summary-label">Average Confidence</div>
            </div>
          </div>

          {/* Abstention Trust Banner */}
          <div className="card" style={{ background: 'var(--accent-bg)', borderColor: 'var(--border-color)', padding: '12px 16px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Shield size={20} style={{ color: 'var(--accent-blue)' }} />
            <div style={{ fontSize: '0.86rem' }}>
              <strong>{abstainedCount} facets not scored</strong> — Withheld because conversational evidence was insufficient.
            </div>
          </div>

          {/* Controls: Search, Filter, Sort */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 2fr 1fr', gap: '16px', marginBottom: '20px', alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <Search size={15} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Search facets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-text"
                style={{ paddingLeft: '32px', width: '100%' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-input)', padding: '3px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              {['All', 'Scored', 'Abstained'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setStatusFilter(tab)}
                  style={{
                    flex: 1,
                    padding: '4px 10px',
                    borderRadius: '4px',
                    border: 'none',
                    background: statusFilter === tab ? 'var(--accent-bg)' : 'transparent',
                    color: statusFilter === tab ? 'var(--accent-blue)' : 'var(--text-secondary)',
                    fontWeight: statusFilter === tab ? 700 : 500,
                    fontSize: '0.78rem',
                    cursor: 'pointer'
                  }}
                >
                  {tab}
                </button>
              ))}
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-select"
              style={{ width: '100%' }}
            >
              <option value="Default Order">Sort By: Default</option>
              <option value="Score">Sort By: Score</option>
              <option value="Confidence">Sort By: Confidence</option>
              <option value="Facet Name">Sort By: Facet Name</option>
            </select>
          </div>

          {/* Results Cards List */}
          {filteredResults.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-secondary)' }}>
              No facet results match the selected query filter.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {filteredResults.map((item) => {
                const isScored = item.status === 'scored';
                const isInsufficient = item.status === 'insufficient_evidence';
                const borderAccent = isScored ? 'var(--scored-color)' : isInsufficient ? 'var(--abstain-color)' : 'var(--unobs-color)';

                return (
                  <div key={item.facet} className="card" style={{ borderLeft: `4px solid ${borderAccent}`, position: 'relative' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h4 style={{ fontSize: '1rem', textTransform: 'capitalize' }}>{item.facet}</h4>
                      {isScored && <span className="badge badge-scored">Scored</span>}
                      {isInsufficient && <span className="badge badge-abstain">Insufficient Evidence</span>}
                      {!isScored && !isInsufficient && <span className="badge badge-unobs">Not Observable</span>}
                    </div>

                    <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginTop: '6px' }}>
                      {isScored ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontWeight: 800, fontSize: '1.05rem' }}>{item.score} / 5</span>
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>• {getScoreLabel(item.score)}</span>
                          {renderScoreDots(item.score)}
                        </div>
                      ) : (
                        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: isInsufficient ? 'var(--abstain-color)' : 'var(--unobs-color)' }}>
                          Score: Null ({isInsufficient ? 'Abstained' : 'Unobservable'})
                        </span>
                      )}

                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        Confidence: <strong>{(item.confidence * 100).toFixed(0)}%</strong>
                      </div>
                    </div>

                    <div className="evidence-quote">
                      <strong>{isScored ? 'Evidence' : 'Reason'}:</strong> "{item.evidence || item.reason}"
                    </div>

                    <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'flex-end' }}>
                      <button
                        className="btn-secondary"
                        onClick={() => setSelectedDetail(item)}
                        style={{ fontSize: '0.78rem', padding: '3px 10px' }}
                      >
                        <span>View Details</span>
                        <ChevronRight size={13} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Export Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
            <button className="btn-secondary" onClick={exportJSON}>
              <Download size={14} />
              <span>Download JSON</span>
            </button>
            <button className="btn-secondary" onClick={exportCSV}>
              <Download size={14} />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      )}

      {/* Evidence Context Drawer Modal */}
      {selectedDetail && (
        <div className="modal-overlay" onClick={() => setSelectedDetail(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
              <h3 style={{ textTransform: 'capitalize' }}>Details: {selectedDetail.facet}</h3>
              <button
                onClick={() => setSelectedDetail(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px', fontSize: '0.86rem' }}>
              <div>
                <div><strong>Facet Name:</strong> <code>{selectedDetail.facet}</code></div>
                <div style={{ marginTop: '6px' }}><strong>Status:</strong> <code>{selectedDetail.status}</code></div>
                <div style={{ marginTop: '6px' }}><strong>Score:</strong> <code>{selectedDetail.score ?? 'Null (Abstained)'}</code></div>
                <div style={{ marginTop: '6px' }}><strong>Confidence:</strong> <code>{(selectedDetail.confidence * 100).toFixed(0)}%</code></div>
              </div>
              <div>
                <div><strong>Evidence:</strong> <em>"{selectedDetail.evidence || 'N/A'}"</em></div>
                <div style={{ marginTop: '6px' }}><strong>Reasoning:</strong> <em>"{selectedDetail.reason || 'N/A'}"</em></div>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '6px' }}>Highlighted Evidence Context:</h4>
              <div style={{ background: 'var(--bg-input)', border: '1px solid var(--border-color)', padding: '12px', borderRadius: '6px', fontSize: '0.85rem', lineHeight: 1.6 }}>
                {inputText}
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '6px' }}>Raw Payload:</h4>
              <pre style={{ background: 'var(--bg-input)', padding: '10px', borderRadius: '6px', fontSize: '0.75rem', overflowX: 'auto', border: '1px solid var(--border-color)' }}>
                {JSON.stringify(selectedDetail, null, 2)}
              </pre>
            </div>

            <div style={{ textAlign: 'right' }}>
              <button className="btn-secondary" onClick={() => setSelectedDetail(null)}>
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
