import React from 'react';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

export default function SafetyView() {
  const examples = [
    {
      category: "Unobservable State",
      input: "I feel dizzy when I wake up in the morning.",
      result: "Abstained (Null)",
      reason: "Internal subjective feeling without external measurable behavioral proof in conversation."
    },
    {
      category: "Sarcasm / Irony",
      input: "I absolutely LOVE presenting to 500 people... my heart was racing and I felt like throwing up.",
      result: "Abstained / Corrected",
      reason: "Literal text presents positive sentiment ('LOVE') but physiological panic proof invalidates literal rating."
    },
    {
      category: "Third-Person Quote",
      input: "My manager said I handled the presentation effectively.",
      result: "Abstained (Null)",
      reason: "Direct evidence evaluates candidate's actions, not third-person hearsay quotes."
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <h2>Safety & Abstention</h2>
        <p className="subtitle">Understand when the system chooses not to make an unsupported conclusion.</p>
      </div>

      <div className="card" style={{ marginBottom: '24px', borderLeft: '4px solid var(--accent-blue)' }}>
        <h3 style={{ color: 'var(--accent-blue)', marginBottom: '8px' }}>Evidence-First Evaluation Principle</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6 }}>
          The FacetIQ system is strictly engineered to prevent AI hallucinations and ungrounded scoring. When conversational evidence is absent, ambiguous, sarcastic, or unobservable, the model safely abstains with a explicit Null status.
        </p>
      </div>

      <h3 style={{ marginBottom: '12px' }}>Responsible Abstention Scenarios</h3>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Conversation Input</th>
              <th>System Result</th>
              <th>Abstention Reason</th>
            </tr>
          </thead>
          <tbody>
            {examples.map((item, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 700 }}>{item.category}</td>
                <td style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>"{item.input}"</td>
                <td><span className="badge badge-abstain">{item.result}</span></td>
                <td style={{ fontSize: '0.82rem' }}>{item.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
