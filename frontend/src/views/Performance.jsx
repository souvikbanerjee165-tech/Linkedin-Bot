import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  TrendingUp, Plus, DollarSign, MessageSquare, 
  Users, CheckCircle2, Award, Lightbulb, BarChart2 
} from 'lucide-react';

export default function Performance() {
  const [logs, setLogs] = useState([]);
  const [summary, setSummary] = useState(null);
  const [showLogModal, setShowLogModal] = useState(false);
  const [drafts, setDrafts] = useState([]);

  const [newLog, setNewLog] = useState({
    post_draft_id: null,
    post_title: '',
    published_date: new Date().toISOString().split('T')[0],
    period_type: '24h',
    impressions: 0,
    reactions: 0,
    comments: 0,
    reposts: 0,
    profile_visits: 0,
    connection_requests: 0,
    inbound_dms: 0,
    qualified_leads: 0,
    sales_opportunities: 0,
    revenue_attributed: 0.0,
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    Promise.all([
      api.getPerformance(),
      api.getAnalyticsSummary(),
      api.getPosts()
    ]).then(([l, s, d]) => {
      setLogs(l);
      setSummary(s);
      setDrafts(d);
    }).catch(console.error);
  };

  const handleCreateLog = async (e) => {
    e.preventDefault();
    try {
      await api.logPerformance(newLog);
      setShowLogModal(false);
      loadData();
    } catch (err) {
      alert("Error recording performance metrics");
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-indigo-400" />
            Performance & Commercial Attribution
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            Track tangible business outcomes — separating superficial vanity likes from real inbound DMs, qualified calls, and attributed revenue.
          </p>
        </div>

        <button
          onClick={() => setShowLogModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4" />
          Log Post Results (24h / 7d)
        </button>
      </div>

      {/* Attribution KPI Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Total Inbound DMs
            </span>
            <div className="text-2xl font-bold text-white mb-1">
              {summary.total_inbound_dms}
            </div>
            <p className="text-xs text-slate-500">
              Across {summary.total_posts_tracked} recorded posts
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Qualified B2B Leads
            </span>
            <div className="text-2xl font-bold text-indigo-400 mb-1">
              {summary.total_qualified_leads}
            </div>
            <p className="text-xs text-slate-500">
              {summary.opportunity_rate}% qualified-to-opp rate
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Sales Opportunities
            </span>
            <div className="text-2xl font-bold text-emerald-400 mb-1">
              {summary.total_sales_opportunities}
            </div>
            <p className="text-xs text-slate-500">
              Confirmed discovery calls
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Attributed Revenue
            </span>
            <div className="text-2xl font-bold text-white mb-1">
              ${summary.total_revenue_attributed.toLocaleString()}
            </div>
            <p className="text-xs text-slate-500">
              Directly tied to LinkedIn origin
            </p>
          </div>
        </div>
      )}

      {/* Recommended Experiments Engine */}
      {summary && summary.recommended_experiments && (
        <div className="bg-indigo-950/30 border border-indigo-900/40 rounded-2xl p-6 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-indigo-400" />
            Hypothesis-Driven Strategic Experiments
          </h3>
          <div className="space-y-2">
            {summary.recommended_experiments.map((exp, idx) => (
              <div key={idx} className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 flex items-start gap-2.5">
                <span className="text-indigo-400 font-bold">EXP-{idx + 1}:</span>
                {exp}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recorded Performance Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center justify-between">
          <span>Logged Post Performance</span>
          <span className="text-xs text-slate-400 font-normal">{logs.length} snapshots recorded</span>
        </h3>

        {logs.length === 0 ? (
          <p className="text-xs text-slate-500 py-6 text-center">
            No performance logs recorded yet. Use the "Log Post Results" button after publishing to track metrics.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 uppercase border-b border-slate-800 pb-2">
                <tr>
                  <th className="py-2.5 pr-4">Post Title</th>
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3">Period</th>
                  <th className="py-2.5 px-3">Impressions</th>
                  <th className="py-2.5 px-3">Reactions</th>
                  <th className="py-2.5 px-3">Comments</th>
                  <th className="py-2.5 px-3">DMs</th>
                  <th className="py-2.5 px-3">Qualified</th>
                  <th className="py-2.5 pl-3">Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {logs.map(log => (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 pr-4 font-semibold text-white max-w-xs truncate">{log.post_title}</td>
                    <td className="py-3 px-3 font-mono text-slate-400">{log.published_date}</td>
                    <td className="py-3 px-3"><span className="bg-slate-800 px-2 py-0.5 rounded text-[11px]">{log.period_type}</span></td>
                    <td className="py-3 px-3 font-mono">{log.impressions.toLocaleString()}</td>
                    <td className="py-3 px-3 font-mono">{log.reactions}</td>
                    <td className="py-3 px-3 font-mono">{log.comments}</td>
                    <td className="py-3 px-3 font-mono text-indigo-400 font-semibold">{log.inbound_dms}</td>
                    <td className="py-3 px-3 font-mono text-emerald-400 font-semibold">{log.qualified_leads}</td>
                    <td className="py-3 pl-3 font-mono">${log.revenue_attributed}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Performance Log Modal */}
      {showLogModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 max-w-lg w-full space-y-5 animate-scaleUp">
            <h3 className="text-lg font-bold text-white">
              Log Post Performance Snapshot
            </h3>

            <form onSubmit={handleCreateLog} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Post Title / Topic</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 3 Observable Signals Dental Practices Leak"
                  value={newLog.post_title}
                  onChange={e => setNewLog({ ...newLog, post_title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 uppercase">Publish Date</label>
                  <input
                    type="date"
                    value={newLog.published_date}
                    onChange={e => setNewLog({ ...newLog, published_date: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 uppercase">Snapshot Interval</label>
                  <select
                    value={newLog.period_type}
                    onChange={e => setNewLog({ ...newLog, period_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="24h">24 Hours</option>
                    <option value="7d">7 Days</option>
                    <option value="30d">30 Days</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="text-[11px] text-slate-400">Impressions</label>
                  <input
                    type="number"
                    value={newLog.impressions}
                    onChange={e => setNewLog({ ...newLog, impressions: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] text-slate-400">Reactions</label>
                  <input
                    type="number"
                    value={newLog.reactions}
                    onChange={e => setNewLog({ ...newLog, reactions: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] text-slate-400">Comments</label>
                  <input
                    type="number"
                    value={newLog.comments}
                    onChange={e => setNewLog({ ...newLog, comments: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="text-[11px] text-indigo-400 font-semibold">Inbound DMs</label>
                  <input
                    type="number"
                    value={newLog.inbound_dms}
                    onChange={e => setNewLog({ ...newLog, inbound_dms: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-indigo-900/40 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] text-emerald-400 font-semibold">Qualified Leads</label>
                  <input
                    type="number"
                    value={newLog.qualified_leads}
                    onChange={e => setNewLog({ ...newLog, qualified_leads: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-emerald-900/40 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] text-slate-400">Attributed $</label>
                  <input
                    type="number"
                    value={newLog.revenue_attributed}
                    onChange={e => setNewLog({ ...newLog, revenue_attributed: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-medium"
                >
                  Save Metrics
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
