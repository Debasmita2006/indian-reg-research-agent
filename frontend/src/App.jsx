import { useState } from 'react';
import { Search, Loader2, AlertTriangle, BarChart3, Search as SearchIcon } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { runResearch } from './api';
import Dashboard from './Dashboard';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('research');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runResearch(query);
      setResult(data);
    } catch (err) {
      setError('Something went wrong. Is the backend server running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="tabs">
        <button
          className={activeTab === 'research' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('research')}
        >
          <SearchIcon size={16} /> Research
        </button>
        <button
          className={activeTab === 'dashboard' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('dashboard')}
        >
          <BarChart3 size={16} /> Dashboard
        </button>
      </div>

      {activeTab === 'research' && (
        <>
          <h1>Indian Regulatory Research Agent</h1>
          <p className="subtitle">
            Ask about Indian policy, RBI/SEBI regulations, or government notifications
          </p>

          <form onSubmit={handleSubmit} className="query-form">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. What are the recent changes in SEBI mutual fund regulations?"
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? <Loader2 className="spin" size={18} /> : <Search size={18} />}
              {loading ? 'Researching...' : 'Research'}
            </button>
          </form>

          {error && (
            <div className="error-box">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}

          {result && (
            <div className="result-container">
              <div className="eval-badges">
                <span className="badge">Faithfulness: {result.eval_result.faithfulness_score}</span>
                <span className="badge">Relevance: {result.eval_result.relevance_score}</span>
                <span className="badge">Completeness: {result.eval_result.completeness_score}</span>
                <span className="badge">Latency: {result.latency_seconds.toFixed(1)}s</span>
              </div>

              <h2>Report</h2>
              <div className="report-text">
                <ReactMarkdown>{result.final_report}</ReactMarkdown>
              </div>

              {result.eval_result.issues_found && result.eval_result.issues_found.length > 0 && (
                <div className="issues-box">
                  <h3>Issues flagged by evaluator</h3>
                  <ul>
                    {result.eval_result.issues_found.map((issue, i) => (
                      <li key={i}>{issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {activeTab === 'dashboard' && <Dashboard />}
    </div>
  );
}

export default App;