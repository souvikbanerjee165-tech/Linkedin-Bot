import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Sparkles, CheckCircle2, AlertTriangle, Copy, 
  Download, ThumbsUp, RefreshCw, Sliders, Eye, 
  FileText, ArrowRight, ShieldAlert, Award
} from 'lucide-react';

const FORMAT_LABELS = {
  problem_solution: "Problem & Solution",
  concise: "Concise Text",
  story: "Builder's Lesson",
  technical_breakdown: "Technical Architecture",
  demo: "Demonstration-Led",
  commercial: "Commercial Offer"
};

const PILLARS = [
  { id: 1, name: "1. Business problems costing time/money" },
  { id: 2, name: "2. Practical AI demonstrations" },
  { id: 3, name: "3. Behind-the-scenes building lessons" },
  { id: 4, name: "4. Before/after workflow comparisons" },
  { id: 5, name: "5. Industry-specific insights" },
  { id: 6, name: "6. Technical explanations made simple" },
  { id: 7, name: "7. Mistakes, trade-offs, and lessons" },
  { id: 8, name: "8. Verified evidence case studies" },
  { id: 9, name: "9. Contrarian but defensible opinions" },
  { id: 10, name: "10. Soft commercial solution posts" }
];

export default function WritePost() {
  const [ideaPrompt, setIdeaPrompt] = useState(
    "I built a system that analyzes dental practice websites and identifies opportunities to improve their digital workflows. I want to explain why business owners should investigate specific operational problems before buying AI tools."
  );
  const [targetAudience, setTargetAudience] = useState("Agency Founders & Dental Practice Leaders");
  const [selectedProduct, setSelectedProduct] = useState("dental_sales_intel");
  const [selectedPillar, setSelectedPillar] = useState(1);
  const [voiceMatch, setVoiceMatch] = useState(0.85);

  const [loading, setLoading] = useState(false);
  const [generationResult, setGenerationResult] = useState(null);
  const [activeFormat, setActiveFormat] = useState("problem_solution");
  const [editedText, setEditedText] = useState("");
  const [copied, setCopied] = useState(false);
  const [feedbackSaved, setFeedbackSaved] = useState("");
  const [scoreData, setScoreData] = useState(null);

  const handleGenerate = async (e) => {
    if (e) e.preventDefault();
    if (!ideaPrompt.trim()) return;

    setLoading(true);
    setFeedbackSaved("");
    try {
      const res = await api.generatePost({
        idea_prompt: ideaPrompt,
        product_key: selectedProduct,
        target_audience: targetAudience,
        content_pillar: selectedPillar,
        voice_match_level: voiceMatch,
        commercial_intent: "Attract decision-makers looking to eliminate manual bottlenecks"
      });
      setGenerationResult(res);
      setActiveFormat("problem_solution");
      const defaultText = res.drafts.problem_solution ? res.drafts.problem_solution.full_text : "";
      setEditedText(defaultText);

      // Score
      const draftObj = await api.getPost(res.draft_id);
      setScoreData(draftObj.buyer_score_breakdown);
    } catch (err) {
      alert("Error generating drafts. Please check your connection or settings.");
    } finally {
      setLoading(false);
    }
  };

  const handleFormatChange = (fmtKey) => {
    setActiveFormat(fmtKey);
    if (generationResult && generationResult.drafts[fmtKey]) {
      setEditedText(generationResult.drafts[fmtKey].full_text);
    }
  };

  const handleCopyClipboard = async () => {
    if (!editedText) return;
    try {
      await navigator.clipboard.writeText(editedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveAndRescore = async () => {
    if (!generationResult) return;
    try {
      await api.updatePost(generationResult.draft_id, {
        active_draft_format: activeFormat,
        final_edited_content: editedText,
        status: "review_ready"
      });
      const newScore = await api.scorePost(generationResult.draft_id);
      setScoreData(newScore);
      setFeedbackSaved("Draft saved & score refreshed!");
      setTimeout(() => setFeedbackSaved(""), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleVoiceFeedback = async (tag) => {
    if (!generationResult) return;
    try {
      await api.submitFeedback(generationResult.draft_id, tag);
      setFeedbackSaved(`Calibrated voice profile: "${tag}"`);
      setTimeout(() => setFeedbackSaved(""), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const currentDraft = generationResult ? generationResult.drafts[activeFormat] : null;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="w-8 h-8 text-indigo-400" />
          LinkedIn Post Generator
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Turn a plain-English idea into 6 distinct, grounded LinkedIn drafts with real DeepSeek intelligence and buyer-intent scoring.
        </p>
      </div>

      {/* Input Idea Box */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
            <span>Describe your idea in ordinary language:</span>
            <span className="text-[11px] text-indigo-400 font-normal">Zero-Slop Engine Enforced</span>
          </label>
          <textarea
            rows={3}
            value={ideaPrompt}
            onChange={e => setIdeaPrompt(e.target.value)}
            placeholder="e.g. I analyzed 50 client workflows and found manual lead qualification costs 15 hours weekly..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-white focus:outline-none focus:border-indigo-500 transition leading-relaxed"
          />
        </div>

        {/* Configuration Matrix */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-slate-400 uppercase">Target Audience</label>
            <input
              type="text"
              value={targetAudience}
              onChange={e => setTargetAudience(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-slate-400 uppercase">Product Focus</label>
            <select
              value={selectedProduct}
              onChange={e => setSelectedProduct(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="podleads_ai">PodLeads AI (Agency Lead Gen)</option>
              <option value="dental_sales_intel">Dental Sales Intelligence</option>
              <option value="dental_os_front_desk">Dental OS & Front Desk (Concept)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-slate-400 uppercase">Content Pillar</label>
            <select
              value={selectedPillar}
              onChange={e => setSelectedPillar(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              {PILLARS.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-[11px] font-semibold text-slate-400 uppercase">
              <span>Voice Match</span>
              <span className="text-indigo-400">{Math.round(voiceMatch * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.4"
              max="1.0"
              step="0.05"
              value={voiceMatch}
              onChange={e => setVoiceMatch(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer h-2 bg-slate-950 rounded-lg"
            />
          </div>
        </div>

        {/* Generate Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="flex items-center gap-2.5 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl shadow-lg shadow-indigo-600/25 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Generating 6 Distinct Drafts with DeepSeek...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate 6 Draft Formats
              </>
            )}
          </button>
        </div>
      </div>

      {/* Generated Content Workspace */}
      {generationResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Draft Area (2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Format Tabs */}
            <div className="flex flex-wrap gap-1.5 bg-slate-900 border border-slate-800 p-1.5 rounded-2xl">
              {Object.keys(generationResult.drafts).map(fmtKey => (
                <button
                  key={fmtKey}
                  onClick={() => handleFormatChange(fmtKey)}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold transition ${
                    activeFormat === fmtKey
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {FORMAT_LABELS[fmtKey] || fmtKey}
                </button>
              ))}
            </div>

            {/* Claims Verification Warning Box */}
            {currentDraft && currentDraft.claims_to_verify && currentDraft.claims_to_verify.length > 0 && (
              <div className="bg-amber-950/30 border border-amber-900/50 rounded-2xl p-4 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  Claims Requiring Your Verification Before Publishing:
                </div>
                <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                  {currentDraft.claims_to_verify.map((claim, idx) => (
                    <li key={idx}>{claim}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Editor Workspace */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex flex-wrap justify-between items-center gap-2 text-xs text-slate-400 pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-200">Active Format:</span>
                  <span className="text-indigo-400 font-mono">{FORMAT_LABELS[activeFormat]}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span>Words: <strong className="text-white">{editedText.split(/\s+/).filter(Boolean).length}</strong></span>
                  <span>Characters: <strong className="text-white">{editedText.length}</strong></span>
                </div>
              </div>

              {/* Editable Text Area */}
              <textarea
                rows={14}
                value={editedText}
                onChange={e => setEditedText(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 font-sans leading-relaxed"
              />

              {/* Visual Suggestion Tag */}
              {currentDraft && currentDraft.suggested_visual && (
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 flex items-start gap-2.5">
                  <Eye className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-white">Recommended Supporting Visual:</strong> {currentDraft.suggested_visual}
                  </div>
                </div>
              )}

              {/* Voice Feedback Tagging Buttons */}
              <div className="space-y-2 pt-2">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Calibrate Writing Style (Select how this draft sounds):
                </div>
                <div className="flex flex-wrap gap-2">
                  {[
                    "Sounds like me",
                    "Too formal",
                    "Too promotional",
                    "Too generic",
                    "Too technical",
                    "Good to publish"
                  ].map(tag => (
                    <button
                      key={tag}
                      onClick={() => handleVoiceFeedback(tag)}
                      className="px-3 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs rounded-lg transition"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
                {feedbackSaved && (
                  <p className="text-xs text-emerald-400 font-medium">{feedbackSaved}</p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap justify-between items-center gap-3 pt-4 border-t border-slate-800">
                <button
                  onClick={handleSaveAndRescore}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl transition"
                >
                  Save Edits & Refresh Score
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopyClipboard}
                    className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition"
                  >
                    <Copy className="w-4 h-4" />
                    {copied ? "Copied for LinkedIn!" : "Copy for LinkedIn Composer"}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Buyer-Intent Scorecard (1 col) */}
          <div className="space-y-6">
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-6 sticky top-6">
              <div className="flex justify-between items-center">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-indigo-400" />
                  Buyer-Intent Scorecard
                </h3>
                {scoreData && (
                  <span className="text-2xl font-extrabold text-indigo-400 font-mono">
                    {scoreData.total_score}
                    <span className="text-xs font-normal text-slate-400">/100</span>
                  </span>
                )}
              </div>

              {scoreData ? (
                <div className="space-y-4">
                  {/* Category Progress Bars */}
                  <div className="space-y-3 text-xs">
                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Audience Relevance</span>
                        <span className="font-mono text-indigo-400">{scoreData.audience_relevance}/20</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${(scoreData.audience_relevance / 20) * 100}%` }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Problem Specificity</span>
                        <span className="font-mono text-indigo-400">{scoreData.problem_specificity}/20</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${(scoreData.problem_specificity / 20) * 100}%` }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Evidence & Credibility</span>
                        <span className="font-mono text-indigo-400">{scoreData.evidence_credibility}/20</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${(scoreData.evidence_credibility / 20) * 100}%` }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Originality & Usefulness</span>
                        <span className="font-mono text-indigo-400">{scoreData.originality_usefulness}/15</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${(scoreData.originality_usefulness / 15) * 100}%` }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Readability & Pacing</span>
                        <span className="font-mono text-indigo-400">{scoreData.readability}/10</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${(scoreData.readability / 10) * 100}%` }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Commercial Relevance</span>
                        <span className="font-mono text-indigo-400">{scoreData.commercial_relevance}/10</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${(scoreData.commercial_relevance / 10) * 100}%` }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Call to Action Quality</span>
                        <span className="font-mono text-indigo-400">{scoreData.cta_quality}/5</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${(scoreData.cta_quality / 5) * 100}%` }} />
                      </div>
                    </div>
                  </div>

                  {/* Actionable Improvements */}
                  <div className="pt-3 border-t border-slate-800 space-y-2">
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Actionable Improvements
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-400">
                      {scoreData.actionable_improvements && scoreData.actionable_improvements.map((imp, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-indigo-400 font-bold">•</span>
                          {imp}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <p className="text-[10px] text-slate-500 italic pt-2 border-t border-slate-800/60">
                    {scoreData.viral_disclaimer}
                  </p>
                </div>
              ) : (
                <p className="text-xs text-slate-500 py-4 text-center">
                  Score breakdown will appear once drafts are generated.
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
