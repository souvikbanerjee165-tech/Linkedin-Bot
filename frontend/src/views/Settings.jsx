import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  Settings as SettingsIcon, ShieldCheck, DollarSign, 
  Database, RefreshCw, CheckCircle2, AlertTriangle, Key 
} from 'lucide-react';

export default function Settings() {
  const [status, setStatus] = useState(null);
  const [backupStatus, setBackupStatus] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = () => {
    api.getStatus().then(setStatus).catch(console.error);
  };

  const handleCreateBackup = async () => {
    setLoading(true);
    setBackupStatus('');
    try {
      const res = await api.createBackup();
      setBackupStatus(`Database backup successfully saved to: ${res.backup_path}`);
    } catch (err) {
      alert("Error generating database backup");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-8 h-8 text-indigo-400" />
          Settings & System Governance
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Manage your DeepSeek integration, token accounting, and local database backups.
        </p>
      </div>

      {/* Grid: DeepSeek API & Cost Accounting */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* DeepSeek API Card */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Key className="w-4 h-4 text-indigo-400" />
            Official DeepSeek API Integration
          </h3>

          <div className="space-y-3 text-xs text-slate-300">
            <div className="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400">Server Key Status:</span>
              <span className={`font-semibold flex items-center gap-1.5 ${
                status && status.is_api_key_configured ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                {status && status.is_api_key_configured ? (
                  <><CheckCircle2 className="w-3.5 h-3.5" /> DEEPSEEK_API_KEY Configured</>
                ) : (
                  <><AlertTriangle className="w-3.5 h-3.5" /> Key Not Detected in .env</>
                )}
              </span>
            </div>

            <div className="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400">Active Model Identifier:</span>
              <span className="font-mono text-indigo-400 font-semibold">
                {status ? status.current_model : 'deepseek-chat'}
              </span>
            </div>

            <div className="text-[11px] text-slate-500 leading-normal p-2">
              <strong className="text-slate-400 block mb-1">Security Guarantee:</strong>
              Your API key is never exposed to browser storage or JavaScript clients. All authentication occurs on the server. To update your key, edit <code>.env</code> in the project directory.
            </div>
          </div>
        </div>

        {/* Cost & Token Accounting */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-indigo-400" />
            Estimated API Usage & Cost
          </h3>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-500 block mb-1 font-semibold">TOTAL API CALLS</span>
              <span className="text-xl font-bold text-white font-mono">
                {status ? status.total_calls : 0}
              </span>
            </div>

            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-500 block mb-1 font-semibold">ESTIMATED SPEND</span>
              <span className="text-xl font-bold text-emerald-400 font-mono">
                ${status ? status.total_cost_usd.toFixed(5) : '0.00000'}
              </span>
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs space-y-1.5">
            <div className="flex justify-between text-slate-400">
              <span>Prompt Tokens Logged:</span>
              <span className="font-mono text-slate-200">{status ? status.total_prompt_tokens.toLocaleString() : 0}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Completion Tokens:</span>
              <span className="font-mono text-slate-200">{status ? status.total_completion_tokens.toLocaleString() : 0}</span>
            </div>
            <div className="flex justify-between text-indigo-400 font-semibold pt-1 border-t border-slate-800/80">
              <span>Total Tokens:</span>
              <span className="font-mono">{status ? status.total_tokens.toLocaleString() : 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Database Backup & Restore */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Database className="w-4 h-4 text-indigo-400" />
          Local Storage & Backup Mechanism
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed max-w-2xl">
          The application operates local-first using SQLite. You can generate instant timestamped database snapshots to prevent data loss across updates.
        </p>

        <div className="flex items-center gap-3">
          <button
            onClick={handleCreateBackup}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Create Immediate Database Backup
          </button>
        </div>

        {backupStatus && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs rounded-xl flex items-center gap-2 font-mono">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            {backupStatus}
          </div>
        )}
      </div>

      {/* Zero-Hallucination Policy */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Factual Verification Standard & AI Policy
        </h3>
        <ul className="text-xs text-slate-400 space-y-2 list-disc list-inside leading-relaxed">
          <li><strong>No Fabricated Case Studies:</strong> The AI will never invent client names, revenue numbers, or testimonials.</li>
          <li><strong>Concept vs Production:</strong> Concept features in Dental Operating System are strictly flagged so they are never advertised as live deployments.</li>
          <li><strong>Human Review Required:</strong> You remain the author and final reviewer. All generated copy should be proofread before posting on LinkedIn.</li>
        </ul>
      </div>
    </div>
  );
}
