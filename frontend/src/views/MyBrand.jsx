import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  User, CheckCircle2, AlertTriangle, ShieldCheck, 
  ExternalLink, Sparkles, Save, Layers, Award
} from 'lucide-react';

export default function MyBrand() {
  const [brand, setBrand] = useState(null);
  const [products, setProducts] = useState([]);
  const [audit, setAudit] = useState(null);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState('');
  const [activeTab, setActiveTab] = useState('profile'); // profile | products | audit

  useEffect(() => {
    Promise.all([
      api.getBrand(),
      api.getProducts(),
      api.getProfileAudit()
    ]).then(([b, p, a]) => {
      setBrand(b);
      setProducts(p);
      setAudit(a);
    }).catch(console.error);
  }, []);

  const handleSaveBrand = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await api.updateBrand(brand);
      setBrand(updated);
      setSavedMessage('Brand profile successfully saved!');
      setTimeout(() => setSavedMessage(''), 3000);
    } catch (err) {
      alert('Error saving brand profile');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateProduct = async (key, updates) => {
    try {
      const updated = await api.updateProduct(key, updates);
      setProducts(products.map(p => p.product_key === key ? updated : p));
    } catch (err) {
      console.error(err);
    }
  };

  if (!brand) return <div className="p-8 text-center text-slate-500">Loading brand profile...</div>;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Personal Brand & Product Matrix
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Ground your LinkedIn positioning in verified facts, demonstrated software, and clear buyer outcomes.
          </p>
        </div>

        {/* Tab switchers */}
        <div className="flex bg-slate-900 border border-slate-800 rounded-xl p-1 gap-1">
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'profile' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Profile Information
          </button>
          <button
            onClick={() => setActiveTab('products')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'products' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Verified Products ({products.length})
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'audit' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Positioning Audit
          </button>
        </div>
      </div>

      {/* TAB 1: Profile Information */}
      {activeTab === 'profile' && (
        <form onSubmit={handleSaveBrand} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          {savedMessage && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm rounded-xl flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              {savedMessage}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                LinkedIn Profile URL
              </label>
              <input
                type="text"
                value={brand.linkedin_url || ''}
                onChange={e => setBrand({ ...brand, linkedin_url: e.target.value })}
                placeholder="https://linkedin.com/in/yourprofile"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 transition"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Target Geographic Markets
              </label>
              <input
                type="text"
                value={brand.target_markets || ''}
                onChange={e => setBrand({ ...brand, target_markets: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 transition"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Current LinkedIn Headline
            </label>
            <input
              type="text"
              value={brand.headline || ''}
              onChange={e => setBrand({ ...brand, headline: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 transition"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              About Section / Background Bio
            </label>
            <textarea
              rows={4}
              value={brand.about_text || ''}
              onChange={e => setBrand({ ...brand, about_text: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-white focus:outline-none focus:border-indigo-500 transition font-sans leading-relaxed"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Verified Technical Skills & Systems
              </label>
              <textarea
                rows={3}
                value={brand.skills || ''}
                onChange={e => setBrand({ ...brand, skills: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Services & Implementation Offers
              </label>
              <textarea
                rows={3}
                value={brand.current_services || ''}
                onChange={e => setBrand({ ...brand, current_services: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                Topics to Discuss
              </label>
              <textarea
                rows={3}
                value={brand.topics_to_discuss || ''}
                onChange={e => setBrand({ ...brand, topics_to_discuss: e.target.value })}
                className="w-full bg-slate-950 border border-emerald-900/30 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-emerald-500 transition"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Topics to Avoid (Anti-Hype Guardrails)
              </label>
              <textarea
                rows={3}
                value={brand.topics_to_avoid || ''}
                onChange={e => setBrand({ ...brand, topics_to_avoid: e.target.value })}
                className="w-full bg-slate-950 border border-rose-900/30 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-rose-500 transition"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-indigo-600/20"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving Changes...' : 'Save Brand Settings'}
            </button>
          </div>
        </form>
      )}

      {/* TAB 2: Verified Products Matrix */}
      {activeTab === 'products' && (
        <div className="space-y-6">
          <div className="bg-indigo-950/40 border border-indigo-900/40 rounded-2xl p-4 text-xs text-indigo-300 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-white block font-medium mb-0.5">Strict Factual Grounding Rule</strong>
              Never claim a feature is production-ready merely because it appears in a project description. Features are strictly demarcated between <strong className="text-emerald-400">Live Verified Capabilities</strong> and <strong className="text-amber-400">Concept / In-Development</strong>.
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6">
            {products.map(p => (
              <div key={p.product_key} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      {p.name}
                      <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                        {p.product_key}
                      </span>
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">{p.tagline}</p>
                  </div>
                  <div className="text-xs text-slate-400">
                    Target: <span className="text-slate-200 font-medium">{p.target_audience}</span>
                  </div>
                </div>

                <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                  {p.description}
                </p>

                {/* Capability Breakdown Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  {/* Verified Capabilities */}
                  <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-xl p-4 space-y-2">
                    <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Live Verified Capabilities
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {p.verified_capabilities.map((vc, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">•</span>
                          {vc}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Concept Capabilities */}
                  <div className="bg-amber-950/20 border border-amber-900/30 rounded-xl p-4 space-y-2">
                    <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Concept / Roadmap (Requires Verification)
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {p.concept_capabilities.map((cc, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-amber-400 font-bold">•</span>
                          {cc}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="text-xs text-slate-400 border-t border-slate-800/80 pt-3">
                  <strong>Validation Status:</strong> {p.metrics_case_studies}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: Positioning Audit */}
      {activeTab === 'audit' && audit && (
        <div className="space-y-8">
          {/* Audit Score Hero */}
          <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/30 rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="space-y-2">
              <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                PROFILE INTELLIGENCE AUDIT
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-white">
                Recommended Direction: {audit.recommended_positioning}
              </h2>
              <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
                {audit.buyer_relevance_summary}
              </p>
            </div>
            <div className="text-center bg-slate-950/80 border border-indigo-500/30 p-5 rounded-2xl min-w-[140px]">
              <div className="text-3xl font-extrabold text-indigo-400">
                {audit.overall_score}
                <span className="text-base font-normal text-slate-400">/100</span>
              </div>
              <div className="text-[11px] text-slate-400 uppercase tracking-wider mt-1 font-semibold">
                Buyer Impact Score
              </div>
            </div>
          </div>

          {/* 3 Positioning Options Cards */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              Strategic Positioning Evaluation
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {audit.positioning_options.map(opt => (
                <div 
                  key={opt.option_key}
                  className={`rounded-2xl p-5 border flex flex-col justify-between transition ${
                    opt.option_key === 'A'
                      ? 'bg-indigo-950/30 border-indigo-500/50 shadow-lg shadow-indigo-900/20'
                      : 'bg-slate-900/60 border-slate-800'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                        OPTION {opt.option_key}
                      </span>
                      <span className="text-xs font-bold text-white">
                        {opt.fit_score}% Fit
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-white">
                      {opt.title}
                    </h4>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {opt.primary_value_prop}
                    </p>
                    <div className="text-[11px] text-indigo-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
                      <strong>Verdict:</strong> {opt.recommendation_reason}
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                    Target: {opt.target_market}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Headline Recommendations */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Award className="w-4 h-4 text-indigo-400" />
              Recommended LinkedIn Headlines
            </h3>
            <div className="space-y-3">
              {audit.headline_alternatives.map((hl, idx) => (
                <div key={idx} className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs font-semibold text-indigo-400">{hl.angle}</div>
                  <p className="text-sm text-slate-200 font-medium select-all">{hl.headline}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Rewritten About Section */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              Suggested About Section Rewrite (Buyer-Centric)
            </h3>
            <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-950/80 p-5 rounded-xl border border-slate-800 select-all">
              {audit.rewritten_about_section}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
