import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { 
  Calendar as CalendarIcon, Download, RefreshCw, 
  Sparkles, CheckCircle2, Clock, Filter 
} from 'lucide-react';

export default function ContentCalendar({ onDraftPost }) {
  const [calendar, setCalendar] = useState([]);
  const [loading, setLoading] = useState(false);
  const [daysCount, setDaysCount] = useState(7);

  useEffect(() => {
    loadCalendar();
  }, []);

  const loadCalendar = () => {
    api.getCalendar().then(setCalendar).catch(console.error);
  };

  const handleGenerate = async (days) => {
    setLoading(true);
    setDaysCount(days);
    try {
      const generated = await api.generateCalendar({ days_count: days });
      setCalendar(generated);
    } catch (err) {
      alert("Error generating content plan");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (id, newStatus) => {
    try {
      const updated = await api.updateCalendarItem(id, { status: newStatus });
      setCalendar(calendar.map(c => c.id === id ? updated : c));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header & Generator Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <CalendarIcon className="w-8 h-8 text-indigo-400" />
            B2B Content Strategy Calendar
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Structured 7-day and 30-day schedules rotating across 10 buyer-focused content pillars.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => handleGenerate(7)}
            disabled={loading}
            className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/20 transition flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Generate 7-Day Plan
          </button>
          <button
            onClick={() => handleGenerate(30)}
            disabled={loading}
            className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition"
          >
            Generate 30-Day Plan
          </button>
          <a
            href={api.getCalendarCsvUrl()}
            download
            className="px-3.5 py-2 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
          </a>
        </div>
      </div>

      {/* Calendar List */}
      {calendar.length === 0 ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center space-y-4">
          <CalendarIcon className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No content plan active</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Click "Generate 7-Day Plan" above to build a strategic posting sequence mapped to your target B2B audiences.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {calendar.map((item, index) => (
            <div
              key={item.id || index}
              className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
            >
              <div className="space-y-2 max-w-3xl">
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="font-mono text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-md font-semibold">
                    {item.scheduled_date} (Day {item.day_number || index + 1})
                  </span>
                  <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[11px] font-medium">
                    {item.pillar_name}
                  </span>
                  <span className="text-slate-500">
                    Format: <strong className="text-slate-400">{item.recommended_format}</strong>
                  </span>
                </div>

                <h3 className="text-base font-bold text-white">
                  "{item.hook_idea}"
                </h3>

                <p className="text-xs text-slate-300 leading-relaxed">
                  <strong className="text-indigo-400">Core Argument:</strong> {item.core_argument}
                </p>

                <div className="flex flex-wrap gap-4 text-[11px] text-slate-400 pt-1">
                  <div>
                    <strong>Target Reader:</strong> {item.target_reader}
                  </div>
                  <div>
                    <strong>Evidence Needed:</strong> {item.evidence_needed}
                  </div>
                </div>
              </div>

              {/* Status and Action Buttons */}
              <div className="flex flex-row md:flex-col items-end gap-2.5 w-full md:w-auto justify-between md:justify-start pt-3 md:pt-0 border-t md:border-t-0 border-slate-800">
                <select
                  value={item.status}
                  onChange={e => handleUpdateStatus(item.id, e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
                >
                  <option value="scheduled">Scheduled</option>
                  <option value="drafted">Drafted</option>
                  <option value="approved">Approved</option>
                  <option value="published">Published</option>
                  <option value="skipped">Skipped</option>
                </select>

                <button
                  onClick={() => onDraftPost && onDraftPost(item.hook_idea)}
                  className="px-3.5 py-1.5 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 rounded-lg text-xs font-medium transition flex items-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Write Draft
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
