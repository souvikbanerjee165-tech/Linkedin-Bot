import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  BookOpen, Plus, ExternalLink, Bookmark, 
  HelpCircle, AlertCircle, Tag, Search 
} from 'lucide-react';

export default function Research() {
  const [researchItems, setResearchItems] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [radarPostText, setRadarPostText] = useState('');
  const [radarPosterRole, setRadarPosterRole] = useState('Agency Founder');
  const [radarAnalyzing, setRadarAnalyzing] = useState(false);
  const [radarResult, setRadarResult] = useState(null);
  const [copiedCommentIdx, setCopiedCommentIdx] = useState(null);

  const [newItem, setNewItem] = useState({
    title: '',
    source_url: '',
    source_type: 'article',
    raw_excerpt: '',
    analyst_notes: '',
    synthesized_problems: '',
    buyer_questions: '',
    industry_vocabulary: '',
    tags: ''
  });

  useEffect(() => {
    loadResearch();
  }, []);

  const loadResearch = () => {
    api.getResearch().then(setResearchItems).catch(console.error);
  };

  const handleCreateResearch = async (e) => {
    e.preventDefault();
    if (!newItem.title) return;
    try {
      await api.createResearch(newItem);
      setShowAddModal(false);
      setNewItem({
        title: '',
        source_url: '',
        source_type: 'article',
        raw_excerpt: '',
        analyst_notes: '',
        synthesized_problems: '',
        buyer_questions: '',
        industry_vocabulary: '',
        tags: ''
      });
      loadResearch();
    } catch (err) {
      alert("Error adding research note");
    }
  };

  const handleAnalyzeDiscussion = async () => {
    if (!radarPostText.trim()) return;
    setRadarAnalyzing(true);
    try {
      const res = await api.analyzeDiscussion({
        post_content: radarPostText,
        poster_role: radarPosterRole,
        target_product: "dental_sales_intel"
      });
      setRadarResult(res);
    } catch (err) {
      alert("Error analyzing post: " + (err.message || err));
    } finally {
      setRadarAnalyzing(false);
    }
  };

  const handleCopyComment = async (text, idx) => {
    await navigator.clipboard.writeText(text);
    setCopiedCommentIdx(idx);
    setTimeout(() => setCopiedCommentIdx(null), 2000);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <BookOpen className="w-8 h-8 text-indigo-400" />
            B2B Content Research & Feed Radar
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            Store industry reports, competitor analyses, and turn trending competitor posts into authoritative inbound comments.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4" />
          Add Research Note
        </button>
      </div>

      {/* Feed & Discussion Radar (Inspired by LinkedIntel) */}
      <div className="bg-slate-900/80 border border-indigo-900/40 rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
            <Search className="w-4 h-4 text-indigo-400" />
            Discussion Radar: Break Down Trending Posts & Draft High-Authority Comments
          </div>
          <span className="text-[11px] text-slate-400 font-mono">LinkedIntel Engine</span>
        </div>

        <p className="text-xs text-slate-300">
          Paste a viral or competitor post from LinkedIn. The radar identifies the underlying commercial vulnerability and drafts 3 high-credibility comments (Builder Reality, Technical Clarification, Tactical Question) that drive profile visits.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="md:col-span-3">
            <textarea
              rows={3}
              placeholder="Paste LinkedIn post text to analyze..."
              value={radarPostText}
              onChange={e => setRadarPostText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div className="space-y-2 flex flex-col justify-between">
            <div>
              <label className="text-[11px] font-semibold text-slate-400 uppercase">Poster Profile / Title</label>
              <input
                type="text"
                value={radarPosterRole}
                onChange={e => setRadarPosterRole(e.target.value)}
                placeholder="e.g. Agency CEO"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white"
              />
            </div>
            <button
              onClick={handleAnalyzeDiscussion}
              disabled={radarAnalyzing || !radarPostText.trim()}
              className="w-full px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl transition"
            >
              {radarAnalyzing ? "Analyzing Thesis..." : "Analyze & Draft Comments"}
            </button>
          </div>
        </div>

        {radarResult && (
          <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-4 text-xs space-y-3 animate-fadeIn">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pb-3 border-b border-slate-800">
              <div>
                <span className="text-slate-400 font-semibold block text-[11px]">Core Thesis:</span>
                <span className="text-slate-200">{radarResult.core_thesis}</span>
              </div>
              <div>
                <span className="text-rose-400 font-semibold block text-[11px]">Commercial Vulnerability:</span>
                <span className="text-slate-200">{radarResult.target_vulnerability}</span>
              </div>
            </div>

            <div className="space-y-2.5">
              <span className="text-indigo-400 font-bold uppercase tracking-wider block text-[11px]">
                High-Authority Response Comments (Click to Copy):
              </span>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {radarResult.comments?.map((c, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleCopyComment(c.text, idx)}
                    className="p-3 bg-slate-900 border border-slate-800 hover:border-indigo-500/50 rounded-xl cursor-pointer transition flex flex-col justify-between space-y-2 group"
                  >
                    <div>
                      <span className="text-[10px] uppercase font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                        {c.style}
                      </span>
                      <p className="text-slate-300 text-xs mt-2 group-hover:text-white leading-relaxed">
                        "{c.text}"
                      </p>
                    </div>
                    <span className="text-[10px] text-slate-500 group-hover:text-indigo-400 font-mono text-right">
                      {copiedCommentIdx === idx ? "Copied!" : "Click to copy"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Grid of Research Notes */}
      {researchItems.length === 0 ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <Bookmark className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No research notes recorded</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Save industry studies, competitor talking points, or questions asked by agency founders to extract recurring buyer friction points.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {researchItems.map(item => (
            <div key={item.id} className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex justify-between items-start gap-2">
                  <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded capitalize">
                    {item.source_type}
                  </span>
                  {item.source_url && (
                    <a
                      href={item.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
                    >
                      Source Link <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                <h3 className="text-base font-bold text-white">
                  {item.title}
                </h3>

                {item.raw_excerpt && (
                  <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 italic border-l-2 border-l-indigo-500">
                    "{item.raw_excerpt}"
                  </div>
                )}

                {item.synthesized_problems && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider block">
                      Core Buyer Problem Discovered:
                    </span>
                    <p className="text-xs text-slate-300">
                      {item.synthesized_problems}
                    </p>
                  </div>
                )}

                {item.buyer_questions && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider block">
                      Recurring Questions Asked:
                    </span>
                    <p className="text-xs text-slate-300">
                      {item.buyer_questions}
                    </p>
                  </div>
                )}
              </div>

              {item.tags && (
                <div className="pt-3 border-t border-slate-800 flex items-center gap-1.5 text-[11px] text-slate-400">
                  <Tag className="w-3 h-3" />
                  {item.tags}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Research Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 max-w-lg w-full space-y-5 animate-scaleUp">
            <h3 className="text-lg font-bold text-white">
              Add External Research Note
            </h3>

            <form onSubmit={handleCreateResearch} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Agency Outbound Efficiency Survey 2026"
                  value={newItem.title}
                  onChange={e => setNewItem({ ...newItem, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 uppercase">Source Type</label>
                  <select
                    value={newItem.source_type}
                    onChange={e => setNewItem({ ...newItem, source_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="article">Article / Report</option>
                    <option value="competitor_post">Competitor Post Analysis</option>
                    <option value="client_call">Client Discovery Call</option>
                    <option value="discussion">Forum / Community Thread</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 uppercase">Source URL</label>
                  <input
                    type="text"
                    placeholder="https://..."
                    value={newItem.source_url}
                    onChange={e => setNewItem({ ...newItem, source_url: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Sourced Quote / Fact (Citations)</label>
                <textarea
                  rows={2}
                  placeholder="Paste direct sourced excerpt..."
                  value={newItem.raw_excerpt}
                  onChange={e => setNewItem({ ...newItem, raw_excerpt: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Synthesized Buyer Problem</label>
                <textarea
                  rows={2}
                  placeholder="What operational pain point does this reveal?"
                  value={newItem.synthesized_problems}
                  onChange={e => setNewItem({ ...newItem, synthesized_problems: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-medium"
                >
                  Save Research Note
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
