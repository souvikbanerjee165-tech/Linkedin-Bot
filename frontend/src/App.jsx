import React, { useState } from 'react';
import { 
  LayoutDashboard, User, ShieldCheck, Calendar, 
  Sparkles, BookOpen, TrendingUp, Download, Settings, 
  Menu, X, ExternalLink
} from 'lucide-react';

import Overview from './views/Overview';
import MyBrand from './views/MyBrand';
import KnowledgeBase from './views/KnowledgeBase';
import ContentCalendar from './views/ContentCalendar';
import WritePost from './views/WritePost';
import Research from './views/Research';
import Performance from './views/Performance';
import Exports from './views/Exports';
import SettingsView from './views/Settings';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'brand', label: 'My Brand', icon: User },
  { id: 'knowledge', label: 'Knowledge Base', icon: ShieldCheck },
  { id: 'calendar', label: 'Content Calendar', icon: Calendar },
  { id: 'write', label: 'Write a Post', icon: Sparkles, badge: 'Core' },
  { id: 'research', label: 'Research', icon: BookOpen },
  { id: 'performance', label: 'Performance', icon: TrendingUp },
  { id: 'exports', label: 'Exports', icon: Download },
  { id: 'settings', label: 'Settings', icon: Settings }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [prefilledHook, setPrefilledHook] = useState('');

  const handleNavigate = (tab, prefill = '') => {
    setActiveTab(tab);
    if (prefill) {
      setPrefilledHook(prefill);
    }
    setMobileMenuOpen(false);
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar Desktop */}
      <aside className="hidden lg:flex flex-col w-64 bg-slate-900/80 border-r border-slate-800/80 p-5 sticky top-0 h-screen">
        {/* Brand Logo */}
        <div className="flex items-center gap-3 px-2 py-3 mb-6">
          <div className="w-9 h-9 bg-gradient-to-tr from-indigo-600 to-indigo-400 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/30">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-extrabold text-sm tracking-tight text-white block">
              Growth Copilot
            </span>
            <span className="text-[10px] text-indigo-400 font-mono tracking-wider uppercase font-semibold">
              LinkedIn B2B AI
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavigate(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  {item.label}
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono uppercase ${
                    isActive ? 'bg-indigo-700 text-indigo-200' : 'bg-slate-800 text-indigo-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer info */}
        <div className="pt-4 border-t border-slate-800/80 text-[11px] text-slate-500 space-y-1 px-2">
          <div className="flex items-center justify-between">
            <span>Local Engine</span>
            <span className="text-emerald-400 font-mono">Online</span>
          </div>
          <div className="flex items-center justify-between">
            <span>DeepSeek v3</span>
            <span className="text-indigo-400 font-mono">Connected</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar Mobile */}
        <header className="lg:hidden flex items-center justify-between p-4 bg-slate-900 border-b border-slate-800 sticky top-0 z-40">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-sm text-white">Growth Copilot</span>
          </div>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-slate-400 hover:text-white rounded-lg"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-slate-900 border-b border-slate-800 p-4 space-y-1">
            {NAV_ITEMS.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold ${
                    isActive ? 'bg-indigo-600 text-white' : 'text-slate-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
          </div>
        )}

        {/* Primary Page Canvas */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'overview' && <Overview onNavigate={handleNavigate} />}
          {activeTab === 'brand' && <MyBrand />}
          {activeTab === 'knowledge' && <KnowledgeBase />}
          {activeTab === 'calendar' && <ContentCalendar onDraftPost={(hook) => handleNavigate('write', hook)} />}
          {activeTab === 'write' && <WritePost key={prefilledHook} initialIdea={prefilledHook} />}
          {activeTab === 'research' && <Research />}
          {activeTab === 'performance' && <Performance />}
          {activeTab === 'exports' && <Exports />}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
}
