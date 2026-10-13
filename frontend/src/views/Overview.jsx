import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  Sparkles, Calendar, FileText, TrendingUp, MessageSquare, 
  DollarSign, ArrowRight, ShieldCheck, CheckCircle2, AlertCircle 
} from 'lucide-react';

export default function Overview({ onNavigate }) {
  const [status, setStatus] = useState(null);
  const [calendar, setCalendar] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [perfSummary, setPerfSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getStatus(),
      api.getCalendar(),
      api.getPosts(),
      api.getAnalyticsSummary()
    ]).then(([st, cal, dr, perf]) => {
      setStatus(st);
      setCalendar(cal);
      setDrafts(dr);
      setPerfSummary(perf);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  const pendingDrafts = drafts.filter(d => d.status === 'draft' || d.status === 'review_ready');
  const approvedDrafts = drafts.filter(d => d.status === 'approved');
  const upcomingPosts = calendar.slice(0, 3);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-950/70 via-slate-900 to-slate-950 border border-indigo-900/40 rounded-2xl p-6 sm:p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium rounded-full">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified Knowledge Base Active
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              LinkedIn B2B Growth & Sales Copilot
            </h1>
            <p className="text-slate-400 text-sm sm:text-base max-w-2xl">
              Grounded, buyer-centric content strategy for your AI automation systems & sales intelligence tools. No generic influencer hype.
            </p>
          </div>
          <button
            onClick={() => onNavigate('write')}
            className="flex items-center gap-2.5 px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl shadow-lg shadow-indigo-600/25 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <Sparkles className="w-4 h-4" />
            Write Post from Idea
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Qualified Inbound */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium mb-3">
            <span>QUALIFIED LEADS</span>
            <div className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {perfSummary ? perfSummary.total_qualified_leads : 0}
          </div>
          <p className="text-xs text-slate-500">
            From {perfSummary ? perfSummary.total_inbound_dms : 0} inbound conversations
          </p>
        </div>

        {/* Card 2: Drafts Awaiting Review */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium mb-3">
            <span>DRAFTS AWAITING APPROVAL</span>
            <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {pendingDrafts.length}
          </div>
          <p className="text-xs text-slate-500">
            {approvedDrafts.length} approved & ready to post
          </p>
        </div>

        {/* Card 3: Scheduled Content */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium mb-3">
            <span>SCHEDULED SLOTS</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <Calendar className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {calendar.length}
          </div>
          <p className="text-xs text-slate-500">
            Across 10 buyer-focused pillars
          </p>
        </div>

        {/* Card 4: DeepSeek API Cost */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium mb-3">
            <span>API SPEND (DEEPSEEK)</span>
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            ${status ? status.total_cost_usd.toFixed(4) : '0.0000'}
          </div>
          <p className="text-xs text-slate-500">
            {status ? `${status.total_tokens.toLocaleString()} tokens logged` : '0 tokens'}
          </p>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Today's Action & Upcoming Content (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Recommended Action */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-3">
              <Sparkles className="w-4 h-4" />
              Today's Recommended Strategic Action
            </div>
            <h3 className="text-lg font-bold text-white mb-2">
              Publish a Demonstration-Led Teardown on Observable Digital Signals
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed mb-4">
              Your prospective agency buyers respond highest to observable proof. Highlight how <strong className="text-indigo-400">Dental Sales Intelligence</strong> or <strong className="text-indigo-400">PodLeads AI</strong> spots friction points before sales reps send a single message.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => onNavigate('write')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-lg flex items-center gap-2 transition"
              >
                Generate This Post
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => onNavigate('calendar')}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition"
              >
                View Full 30-Day Strategy
              </button>
            </div>
          </div>

          {/* Upcoming Content Queue */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Calendar className="w-4 h-4 text-indigo-400" />
                Upcoming Content Schedule
              </h3>
              <button
                onClick={() => onNavigate('calendar')}
                className="text-indigo-400 hover:text-indigo-300 text-xs font-medium flex items-center gap-1"
              >
                Manage Calendar <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {upcomingPosts.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-sm">
                No scheduled posts yet. Click below to generate your 7-day content schedule.
                <div className="mt-3">
                  <button
                    onClick={() => onNavigate('calendar')}
                    className="px-4 py-2 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 rounded-lg text-xs font-medium hover:bg-indigo-600/30 transition"
                  >
                    Generate Content Plan
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {upcomingPosts.map((item, idx) => (
                  <div key={idx} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                          {item.scheduled_date}
                        </span>
                        <span className="text-xs text-slate-400">
                          {item.pillar_name}
                        </span>
                      </div>
                      <p className="text-sm font-semibold text-white">
                        {item.hook_idea}
                      </p>
                      <p className="text-xs text-slate-400">
                        Target: {item.target_reader}
                      </p>
                    </div>
                    <button
                      onClick={() => onNavigate('write')}
                      className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg whitespace-nowrap transition"
                    >
                      Draft Now
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Drafts & System Health (1 col) */}
        <div className="space-y-6">
          {/* Pending Drafts */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <h3 className="text-base font-bold text-white mb-4 flex items-center justify-between">
              <span>Saved Drafts</span>
              <span className="text-xs text-slate-400 font-normal">{drafts.length} total</span>
            </h3>

            {drafts.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">
                No drafts created yet. Enter an idea on the "Write a Post" tab.
              </p>
            ) : (
              <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
                {drafts.slice(0, 5).map(d => (
                  <div 
                    key={d.id} 
                    onClick={() => onNavigate('write')}
                    className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl hover:border-indigo-500/50 cursor-pointer transition group"
                  >
                    <div className="flex justify-between items-center text-xs mb-1">
                      <span className="text-indigo-400 font-mono">Draft #{d.id}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                        d.status === 'approved' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                      }`}>
                        {d.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 font-medium line-clamp-2 group-hover:text-white transition">
                      {d.idea_prompt}
                    </p>
                    {d.buyer_score_total && (
                      <div className="mt-2 text-[11px] text-slate-400 flex items-center gap-1">
                        Buyer Score: <strong className="text-indigo-400">{d.buyer_score_total}/100</strong>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Model Status Card */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              DeepSeek AI Status
            </h3>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Current Model:</span>
              <span className="font-mono text-white text-xs bg-slate-800 px-2 py-1 rounded">
                {status ? status.current_model : 'deepseek-chat'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">API Connection:</span>
              <span className={`flex items-center gap-1.5 text-xs font-medium ${
                status && status.is_api_key_configured ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                {status && status.is_api_key_configured ? (
                  <><CheckCircle2 className="w-3.5 h-3.5" /> Official API Active</>
                ) : (
                  <><AlertCircle className="w-3.5 h-3.5" /> Offline Sandbox Mode</>
                )}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal">
              {status && status.is_api_key_configured 
                ? "DeepSeek API calls are securely authenticated server-side." 
                : "Add DEEPSEEK_API_KEY in Settings to enable live online inference."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
