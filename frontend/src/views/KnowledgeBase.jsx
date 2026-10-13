import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  ShieldCheck, AlertCircle, Plus, CheckCircle, 
  Trash2, Filter, Tag, Check, HelpCircle 
} from 'lucide-react';

const TIER_COLORS = {
  verified_fact: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    badge: 'bg-emerald-500/20 text-emerald-400',
    label: 'Verified Fact',
    desc: 'Tested, documented software capabilities and verified background.'
  },
  personal_opinion: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    badge: 'bg-blue-500/20 text-blue-400',
    label: 'Personal Opinion',
    desc: 'Individual perspectives, strategy philosophies, and builder viewpoints.'
  },
  reasonable_interpretation: {
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
    badge: 'bg-purple-500/20 text-purple-400',
    label: 'Reasonable Interpretation',
    desc: 'Analysis derived from observable business signals and industry patterns.'
  },
  unverified_hypothesis: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    badge: 'bg-amber-500/20 text-amber-400',
    label: 'Unverified Hypothesis',
    desc: 'Concepts requiring live testing before making marketing assertions.'
  },
  needs_approval: {
    bg: 'bg-rose-500/10',
    border: 'border-rose-500/30',
    badge: 'bg-rose-500/20 text-rose-400',
    label: 'Needs Approval',
    desc: 'Specific metrics, client quotes, or revenue claims requiring explicit user sign-off.'
  }
};

export default function KnowledgeBase() {
  const [items, setItems] = useState([]);
  const [activeTier, setActiveTier] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newItem, setNewItem] = useState({
    category: 'verified_fact',
    title: '',
    claim_content: '',
    evidence_source: '',
    tags: '',
    is_verified: true,
    approved_by_user: true
  });

  useEffect(() => {
    loadItems();
  }, [activeTier]);

  const loadItems = () => {
    api.getKnowledge(activeTier === 'all' ? null : activeTier).then(setItems).catch(console.error);
  };

  const handleCreateItem = async (e) => {
    e.preventDefault();
    if (!newItem.title || !newItem.claim_content) return;
    try {
      await api.createKnowledge(newItem);
      setShowAddModal(false);
      setNewItem({
        category: 'verified_fact',
        title: '',
        claim_content: '',
        evidence_source: '',
        tags: '',
        is_verified: true,
        approved_by_user: true
      });
      loadItems();
    } catch (err) {
      alert('Error creating knowledge item');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this knowledge claim?')) return;
    try {
      await api.deleteKnowledge(id);
      setItems(items.filter(i => i.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleVerify = async (item) => {
    try {
      const updated = await api.updateKnowledge(item.id, {
        is_verified: !item.is_verified,
        approved_by_user: !item.approved_by_user
      });
      setItems(items.map(i => i.id === item.id ? updated : i));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-indigo-400" />
            Personal Brand Knowledge Base
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            A persistent repository distinguishing verified facts, opinions, interpretations, hypotheses, and claims requiring your sign-off.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4" />
          Add Claim / Knowledge
        </button>
      </div>

      {/* 5-Tier Category Filter Pills */}
      <div className="flex flex-wrap gap-2 pt-2">
        <button
          onClick={() => setActiveTier('all')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeTier === 'all'
              ? 'bg-slate-100 text-slate-900 shadow'
              : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          All Categories ({items.length})
        </button>

        {Object.entries(TIER_COLORS).map(([key, config]) => (
          <button
            key={key}
            onClick={() => setActiveTier(key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition border ${
              activeTier === key
                ? `${config.bg} ${config.badge} ${config.border} shadow`
                : 'bg-slate-900/60 text-slate-400 hover:text-white border-slate-800'
            }`}
          >
            {config.label}
          </button>
        ))}
      </div>

      {/* Knowledge Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map(item => {
          const tier = TIER_COLORS[item.category] || TIER_COLORS.verified_fact;
          return (
            <div
              key={item.id}
              className={`bg-slate-900/70 border rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:border-slate-700 transition ${tier.border}`}
            >
              <div className="space-y-3">
                <div className="flex justify-between items-start gap-2">
                  <span className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md ${tier.badge}`}>
                    {tier.label}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleVerify(item)}
                      title={item.is_verified ? "Verified and approved" : "Click to mark as verified"}
                      className={`p-1.5 rounded-lg border transition ${
                        item.is_verified
                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                          : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                      }`}
                    >
                      <Check className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg transition"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <h3 className="text-base font-bold text-white">
                  {item.title}
                </h3>

                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
                  {item.claim_content}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex flex-wrap justify-between items-center text-[11px] text-slate-400 gap-2">
                <div className="flex items-center gap-1.5">
                  <span className="font-semibold text-slate-300">Source:</span>
                  <span className="truncate max-w-[200px]">{item.evidence_source || 'Direct Builder Context'}</span>
                </div>
                {item.tags && (
                  <div className="flex items-center gap-1 text-slate-500">
                    <Tag className="w-3 h-3" />
                    {item.tags}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 max-w-lg w-full space-y-5 animate-scaleUp">
            <h3 className="text-lg font-bold text-white">
              Add Verified Claim or Knowledge Item
            </h3>

            <form onSubmit={handleCreateItem} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Knowledge Tier</label>
                <select
                  value={newItem.category}
                  onChange={e => setNewItem({ ...newItem, category: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="verified_fact">1. Verified Fact (Demonstrated code / verified metrics)</option>
                  <option value="personal_opinion">2. Personal Opinion & Philosophy</option>
                  <option value="reasonable_interpretation">3. Reasonable Interpretation</option>
                  <option value="unverified_hypothesis">4. Unverified Hypothesis</option>
                  <option value="needs_approval">5. Needs Approval (Customer quotes / revenue claims)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Claim Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. PodLeads AI Channel Metadata Extraction"
                  value={newItem.title}
                  onChange={e => setNewItem({ ...newItem, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Claim Statement</label>
                <textarea
                  rows={3}
                  required
                  placeholder="State the verified fact or constraint clearly..."
                  value={newItem.claim_content}
                  onChange={e => setNewItem({ ...newItem, claim_content: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Evidence / Documentation Source</label>
                <input
                  type="text"
                  placeholder="e.g. Codebase repository commit or client audit report"
                  value={newItem.evidence_source}
                  onChange={e => setNewItem({ ...newItem, evidence_source: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase">Tags (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g. podleads, agency, lead_gen"
                  value={newItem.tags}
                  onChange={e => setNewItem({ ...newItem, tags: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
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
                  Save Claim
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
