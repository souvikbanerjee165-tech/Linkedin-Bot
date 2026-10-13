import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Sparkles, CheckCircle2, AlertTriangle, Copy, 
  Download, ThumbsUp, RefreshCw, Sliders, Eye, 
  FileText, ArrowRight, ShieldAlert, Award, Globe, 
  Smartphone, Monitor, Share2, ThumbsUp as LikeIcon,
  MessageCircle, Repeat2, Send
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

  // Playwright URL inspector state
  const [inspectUrl, setInspectUrl] = useState("");
  const [inspecting, setInspecting] = useState(false);
  const [inspectionResult, setInspectionResult] = useState(null);

  // LinkedIn Feed Preview state
  const [previewMode, setPreviewMode] = useState("editor"); // 'editor' | 'desktop' | 'mobile'
  const [expandedPreview, setExpandedPreview] = useState(false);

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
      const chosenFormat = (res.drafts && res.drafts[activeFormat]?.full_text) ? activeFormat : "problem_solution";
      setActiveFormat(chosenFormat);
      const text = (res.drafts && res.drafts[chosenFormat]?.full_text) || (res.drafts && Object.values(res.drafts)[0]?.full_text) || "";
      setEditedText(text);

      // Score
      const draftObj = await api.getPost(res.draft_id);
      setScoreData(draftObj.buyer_score_breakdown);
    } catch (err) {
      alert("Error generating drafts. Please check your connection or settings.");
    } finally {
      setLoading(false);
    }
  };

  const handleRunPlaywrightInspection = async () => {
    if (!inspectUrl.trim()) return;
    setInspecting(true);
    try {
      const signals = await api.inspectUrl(inspectUrl);
      setInspectionResult(signals);
      // Preload hook into the idea box
      const newPrompt = `Website audit of ${signals.target_url}: Found opportunity score of ${signals.opportunity_score}/100. ${signals.outreach_angle} Bottlenecks observed: ${signals.observable_bottlenecks.join('; ')}`;
      setIdeaPrompt(newPrompt);
      setSelectedProduct("dental_sales_intel");
      setSelectedPillar(2); // Practical demonstration
    } catch (err) {
      alert("Error running Playwright audit. Make sure the URL is reachable.");
    } finally {
      setInspecting(false);
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

  // Render truncated text for LinkedIn feed preview
  const lines = editedText.split('\n');
  const previewCutoff = previewMode === 'mobile' ? 4 : 3;
  const isCut = lines.length > previewCutoff && !expandedPreview;
  const displayedText = isCut ? lines.slice(0, previewCutoff).join('\n') : editedText;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="w-8 h-8 text-indigo-400" />
          LinkedIn Post Generator & Feed Preview
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Generate 6 distinct B2B drafts with live DeepSeek AI, audit prospect websites with Playwright, and test mobile/desktop hook cutoffs.
        </p>
      </div>

      {/* Playwright Headless Signal Inspector Banner */}
      <div className="bg-slate-900/80 border border-indigo-900/40 rounded-2xl p-5 sm:p-6 space-y-4">
        <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
          <Globe className="w-4 h-4" />
          Playwright Live Web Signal Inspector (Dental & Agency Sites)
        </div>
        <p className="text-xs text-slate-300">
          Enter a prospect's public website. Playwright headlessly checks for online booking widgets, load speed, contact friction, and generates an audit you can turn directly into a post.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="e.g. https://brightdentalcare.com or any practice URL"
            value={inspectUrl}
            onChange={e => setInspectUrl(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
          />
          <button
            onClick={handleRunPlaywrightInspection}
            disabled={inspecting || !inspectUrl.trim()}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${inspecting ? 'animate-spin' : ''}`} />
            {inspecting ? 'Inspecting with Playwright...' : 'Inspect Site & Preload Post'}
          </button>
        </div>

        {inspectionResult && (
          <div className="bg-slate-950/80 border border-emerald-900/30 rounded-xl p-4 text-xs text-slate-300 space-y-2 animate-fadeIn">
            <div className="flex justify-between items-center text-emerald-400 font-bold">
              <span>Audit Complete for: {inspectionResult.page_title || inspectionResult.target_url}</span>
              <span className="font-mono bg-emerald-500/10 px-2.5 py-0.5 rounded text-emerald-400">
                Opportunity Score: {inspectionResult.opportunity_score}/100
              </span>
            </div>
            <p><strong>Load Speed:</strong> {inspectionResult.load_time_seconds}s | <strong>Interactive Booking:</strong> {inspectionResult.has_interactive_booking ? 'Detected' : 'None (Phone only)'}</p>
            <p className="text-indigo-300 font-medium"><strong>Strategy Angle:</strong> {inspectionResult.outreach_angle}</p>
          </div>
        )}
      </div>

      {/* Input Idea Box */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
            <span>Describe your post idea or core argument:</span>
            <span className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> DeepSeek Live API Active
            </span>
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
            {/* Format Tabs & Preview View Switcher */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div className="flex flex-wrap gap-1.5 bg-slate-900 border border-slate-800 p-1.5 rounded-2xl">
                {Object.keys(generationResult.drafts).map(fmtKey => (
                  <button
                    key={fmtKey}
                    onClick={() => handleFormatChange(fmtKey)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                      activeFormat === fmtKey
                        ? 'bg-indigo-600 text-white shadow'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {FORMAT_LABELS[fmtKey] || fmtKey}
                  </button>
                ))}
              </div>

              {/* View Switcher: Editor vs Desktop Feed vs Mobile Feed */}
              <div className="flex bg-slate-900 border border-slate-800 rounded-xl p-1 gap-1">
                <button
                  onClick={() => setPreviewMode('editor')}
                  className={`px-3 py-1 text-xs font-medium rounded-lg flex items-center gap-1.5 transition ${
                    previewMode === 'editor' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <FileText className="w-3 h-3" />
                  Editor
                </button>
                <button
                  onClick={() => setPreviewMode('desktop')}
                  className={`px-3 py-1 text-xs font-medium rounded-lg flex items-center gap-1.5 transition ${
                    previewMode === 'desktop' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Monitor className="w-3 h-3" />
                  Desktop Feed
                </button>
                <button
                  onClick={() => setPreviewMode('mobile')}
                  className={`px-3 py-1 text-xs font-medium rounded-lg flex items-center gap-1.5 transition ${
                    previewMode === 'mobile' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Smartphone className="w-3 h-3" />
                  Mobile Feed
                </button>
              </div>
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

            {/* EDITOR VIEW */}
            {previewMode === 'editor' && (
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

                <textarea
                  rows={13}
                  value={editedText}
                  onChange={e => setEditedText(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 font-sans leading-relaxed"
                />

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
            )}

            {/* LIVE LINKEDIN FEED PREVIEW (Desktop or Mobile) */}
            {previewMode !== 'editor' && (
              <div className="space-y-4">
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-400 flex items-center justify-between">
                  <span>Simulating <strong>{previewMode === 'mobile' ? 'Mobile App' : 'Desktop Feed'}</strong> cutoff fold:</span>
                  <span className="text-indigo-400 font-medium">
                    {isCut ? `Cutoff at line ${previewCutoff} ("...see more" active)` : 'Full post expanded'}
                  </span>
                </div>

                <div className={`mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl ${
                  previewMode === 'mobile' ? 'max-w-sm' : 'w-full'
                }`}>
                  {/* LinkedIn Post Header */}
                  <div className="flex items-start gap-3 mb-4">
                    <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center font-bold text-white text-sm flex-shrink-0 shadow">
                      YOU
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white leading-tight">
                        Software Builder & Automation Specialist
                      </div>
                      <div className="text-[11px] text-slate-400 leading-tight mt-0.5">
                        Building AI-Powered Business Systems & Sales Intelligence
                      </div>
                      <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
                        <span>Just now</span> • <span>🌐</span>
                      </div>
                    </div>
                  </div>

                  {/* Post Body with Hook Fold */}
                  <div className="text-xs sm:text-sm text-slate-200 font-sans leading-relaxed whitespace-pre-line mb-4">
                    {displayedText}
                    {isCut && (
                      <span
                        onClick={() => setExpandedPreview(true)}
                        className="text-slate-400 hover:text-indigo-400 font-semibold cursor-pointer ml-1 inline-block"
                      >
                        ...see more
                      </span>
                    )}
                  </div>

                  {/* Reaction and Engagement Counters */}
                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 mb-2">
                    <div className="flex items-center gap-1">
                      <span className="bg-indigo-600 text-white rounded-full p-0.5 text-[8px]">👍</span>
                      <span>18 people interested</span>
                    </div>
                    <div>4 comments</div>
                  </div>

                  {/* LinkedIn Action Buttons */}
                  <div className="pt-1 border-t border-slate-800/80 flex justify-between text-slate-400 text-xs px-2">
                    <button className="flex items-center gap-1.5 hover:text-white py-1">
                      <LikeIcon className="w-4 h-4" /> Like
                    </button>
                    <button className="flex items-center gap-1.5 hover:text-white py-1">
                      <MessageCircle className="w-4 h-4" /> Comment
                    </button>
                    <button className="flex items-center gap-1.5 hover:text-white py-1">
                      <Repeat2 className="w-4 h-4" /> Repost
                    </button>
                    <button className="flex items-center gap-1.5 hover:text-white py-1">
                      <Send className="w-4 h-4" /> Send
                    </button>
                  </div>
                </div>

                <div className="flex justify-center pt-2">
                  <button
                    onClick={() => setExpandedPreview(!expandedPreview)}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    {expandedPreview ? "Simulate Fold Again" : "Expand Full Post Preview"}
                  </button>
                </div>
              </div>
            )}
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
