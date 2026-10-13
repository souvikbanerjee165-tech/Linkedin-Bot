import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  Download, FileText, CheckSquare, Square, 
  Calendar, FileCode, CheckCircle2, Copy 
} from 'lucide-react';

export default function Exports() {
  const [drafts, setDrafts] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [copiedDraftId, setCopiedDraftId] = useState(null);

  useEffect(() => {
    api.getPosts().then(d => {
      setDrafts(d);
      // Select all by default up to 7
      setSelectedIds(d.slice(0, 7).map(item => item.id));
    }).catch(console.error);
  }, []);

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === drafts.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(drafts.map(d => d.id));
    }
  };

  const handleCopy = async (draft) => {
    const data = await api.getClipboard(draft.id);
    await navigator.clipboard.writeText(data.clipboard_text);
    setCopiedDraftId(draft.id);
    setTimeout(() => setCopiedDraftId(null), 2500);
  };

  const handleDownloadPdfPack = async () => {
    if (selectedIds.length === 0) {
      alert("Please select at least one post draft.");
      return;
    }
    const res = await fetch(api.getPdfPackUrl(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedIds)
    });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weekly_linkedin_content_pack_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const handleDownloadMarkdownPack = async () => {
    if (selectedIds.length === 0) {
      alert("Please select at least one post draft.");
      return;
    }
    const res = await fetch(api.getMarkdownPackUrl(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedIds)
    });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weekly_linkedin_content_pack_${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Download className="w-8 h-8 text-indigo-400" />
            Exports & Weekly Content Packs
          </h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            Export publish-ready copy directly to your clipboard, or bundle approved drafts into an executive PDF or Markdown pack.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleDownloadPdfPack}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 transition"
          >
            <Download className="w-4 h-4" />
            Download PDF Pack ({selectedIds.length})
          </button>
          <button
            onClick={handleDownloadMarkdownPack}
            className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs rounded-xl transition"
          >
            <FileCode className="w-4 h-4" />
            Download Markdown Pack
          </button>
        </div>
      </div>

      {/* Draft Selection List */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-slate-800 text-xs text-slate-400">
          <button
            onClick={handleSelectAll}
            className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 font-medium"
          >
            {selectedIds.length === drafts.length ? (
              <CheckSquare className="w-4 h-4" />
            ) : (
              <Square className="w-4 h-4" />
            )}
            {selectedIds.length === drafts.length ? 'Deselect All' : 'Select All Posts'}
          </button>

          <span>{selectedIds.length} of {drafts.length} selected for bundle</span>
        </div>

        {drafts.length === 0 ? (
          <p className="text-xs text-slate-500 py-6 text-center">
            No drafts available to export yet. Generate posts from the "Write a Post" tab first.
          </p>
        ) : (
          <div className="space-y-3">
            {drafts.map(d => {
              const isSelected = selectedIds.includes(d.id);
              return (
                <div
                  key={d.id}
                  className={`p-4 rounded-xl border transition flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 ${
                    isSelected
                      ? 'bg-slate-950/80 border-indigo-500/40'
                      : 'bg-slate-950/40 border-slate-800/80 opacity-70'
                  }`}
                >
                  <div className="flex items-start gap-3 max-w-2xl">
                    <button
                      onClick={() => toggleSelect(d.id)}
                      className="mt-0.5 text-indigo-400 hover:text-indigo-300"
                    >
                      {isSelected ? (
                        <CheckSquare className="w-4 h-4" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                    </button>
                    <div>
                      <div className="flex items-center gap-2 text-xs mb-1">
                        <span className="font-mono text-indigo-400">Post #{d.id}</span>
                        <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[10px] uppercase font-semibold">
                          {d.active_draft_format}
                        </span>
                        {d.buyer_score_total && (
                          <span className="text-emerald-400 font-mono text-[11px]">
                            {d.buyer_score_total}/100 Score
                          </span>
                        )}
                      </div>
                      <h4 className="text-sm font-semibold text-white">
                        {d.idea_prompt}
                      </h4>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
                    <button
                      onClick={() => handleCopy(d)}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition flex items-center gap-1.5"
                    >
                      <Copy className="w-3.5 h-3.5" />
                      {copiedDraftId === d.id ? "Copied!" : "Copy Text"}
                    </button>
                    <a
                      href={api.getSinglePdfUrl(d.id)}
                      download
                      className="px-3 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 text-xs rounded-lg transition flex items-center gap-1.5"
                    >
                      <Download className="w-3.5 h-3.5" />
                      PDF
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
