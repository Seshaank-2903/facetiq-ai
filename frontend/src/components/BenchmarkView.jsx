import React, { useState } from 'react';
import { BarChart3, Play, CheckCircle } from 'lucide-react';

export default function BenchmarkView() {
  const [running, setRunning] = useState(false);
  const [evalResult, setEvalResult] = useState(null);

  const runBenchmark = () => {
    setRunning(true);
    fetch('http://127.0.0.1:8000/api/evaluate', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        setEvalResult(data.results);
        setRunning(false);
      })
      .catch(err => {
        console.error('Benchmark evaluation error:', err);
        setRunning(false);
      });
  };

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <h2>Benchmark Evaluation</h2>
        <p className="subtitle">Evaluate system accuracy, recall, and abstention precision against reference ground truth.</p>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3>Run Systematic Evaluation</h3>
            <p className="subtitle">Execute evaluation benchmark suite over test scenarios.</p>
          </div>
          <button className="btn-primary" onClick={runBenchmark} disabled={running}>
            {running ? 'Running Benchmark...' : 'Run Benchmark Evaluation'}
          </button>
        </div>
      </div>

      {evalResult ? (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
            <div className="summary-card">
              <div className="summary-value" style={{ color: 'var(--scored-color)' }}>{(evalResult.precision * 100).toFixed(1)}%</div>
              <div className="summary-label">Scoring Precision</div>
            </div>
            <div className="summary-card">
              <div className="summary-value" style={{ color: 'var(--accent-blue)' }}>{(evalResult.recall * 100).toFixed(1)}%</div>
              <div className="summary-label">Recall</div>
            </div>
            <div className="summary-card">
              <div className="summary-value" style={{ color: 'var(--abstain-color)' }}>{(evalResult.f1_score * 100).toFixed(1)}%</div>
              <div className="summary-label">F1-Score</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{(evalResult.abstention_accuracy * 100).toFixed(1)}%</div>
              <div className="summary-label">Abstention Accuracy</div>
            </div>
          </div>

          <div className="card">
            <h4>Benchmark Details Payload</h4>
            <pre style={{ background: 'var(--bg-input)', padding: '12px', borderRadius: '6px', fontSize: '0.8rem', overflowX: 'auto', marginTop: '10px' }}>
              {JSON.stringify(evalResult, null, 2)}
            </pre>
          </div>
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Click "Run Benchmark Evaluation" to execute tests and view validation performance metrics.
        </div>
      )}
    </div>
  );
}
