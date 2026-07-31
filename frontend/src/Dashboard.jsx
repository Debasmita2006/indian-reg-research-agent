import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getDashboardData } from './api';

function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboardData()
      .then((data) => {
        const formatted = data.map((d, i) => ({
          ...d,
          index: i + 1,
          latency_seconds: d.latency_seconds ? Number(d.latency_seconds.toFixed(1)) : null,
        }));
        setLogs(formatted);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to load dashboard data.');
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading dashboard...</p>;
  if (error) return <p className="error-box">{error}</p>;
  if (logs.length === 0) return <p>No queries logged yet. Run a research query first.</p>;

  const avg = (key) => (logs.reduce((sum, l) => sum + (l[key] || 0), 0) / logs.length).toFixed(2);

  return (
    <div className="dashboard-container">
      <div className="eval-badges">
        <span className="badge">Avg Faithfulness: {avg('faithfulness_score')}</span>
        <span className="badge">Avg Relevance: {avg('relevance_score')}</span>
        <span className="badge">Avg Completeness: {avg('completeness_score')}</span>
        <span className="badge">Avg Latency: {avg('latency_seconds')}s</span>
        <span className="badge">Total Queries: {logs.length}</span>
      </div>

      <h3>Eval Scores Over Time</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={logs}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d38" />
          <XAxis dataKey="index" stroke="#9aa0ac" label={{ value: 'Query #', position: 'insideBottom', offset: -5 }} />
          <YAxis domain={[0, 1]} stroke="#9aa0ac" />
          <Tooltip contentStyle={{ background: '#171923', border: '1px solid #2a2d38' }} />
          <Legend />
          <Line type="monotone" dataKey="faithfulness_score" stroke="#4f7cff" name="Faithfulness" />
          <Line type="monotone" dataKey="relevance_score" stroke="#4fd1a5" name="Relevance" />
          <Line type="monotone" dataKey="completeness_score" stroke="#f5a623" name="Completeness" />
        </LineChart>
      </ResponsiveContainer>

      <h3>Latency Over Time (seconds)</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={logs}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d38" />
          <XAxis dataKey="index" stroke="#9aa0ac" />
          <YAxis stroke="#9aa0ac" />
          <Tooltip contentStyle={{ background: '#171923', border: '1px solid #2a2d38' }} />
          <Line type="monotone" dataKey="latency_seconds" stroke="#e05d5d" name="Latency (s)" />
        </LineChart>
      </ResponsiveContainer>

      <h3>Query Log</h3>
      <table className="log-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Query</th>
            <th>Faithfulness</th>
            <th>Contradictions</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{log.id}</td>
              <td className="query-cell">{log.query}</td>
              <td>{log.faithfulness_score}</td>
              <td>{log.contradictions_found}</td>
              <td>{log.latency_seconds}s</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Dashboard;