const API_BASE = '/api';

export const api = {
  // Brand
  getBrand: () => fetch(`${API_BASE}/brand`).then(r => r.json()),
  updateBrand: (data) => fetch(`${API_BASE}/brand`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  getProfileAudit: () => fetch(`${API_BASE}/brand/audit`).then(r => r.json()),

  // Knowledge Base
  getKnowledge: (category) => fetch(`${API_BASE}/knowledge${category ? `?category=${category}` : ''}`).then(r => r.json()),
  createKnowledge: (data) => fetch(`${API_BASE}/knowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  updateKnowledge: (id, data) => fetch(`${API_BASE}/knowledge/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  deleteKnowledge: (id) => fetch(`${API_BASE}/knowledge/${id}`, { method: 'DELETE' }).then(r => r.json()),

  // Products
  getProducts: () => fetch(`${API_BASE}/products`).then(r => r.json()),
  updateProduct: (key, data) => fetch(`${API_BASE}/products/${key}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  // Posts & Drafting
  generatePost: (payload) => fetch(`${API_BASE}/posts/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(r => r.json()),
  getPosts: () => fetch(`${API_BASE}/posts`).then(r => r.json()),
  getPost: (id) => fetch(`${API_BASE}/posts/${id}`).then(r => r.json()),
  updatePost: (id, data) => fetch(`${API_BASE}/posts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  scorePost: (id) => fetch(`${API_BASE}/posts/${id}/score`, { method: 'POST' }).then(r => r.json()),
  submitFeedback: (id, tag) => fetch(`${API_BASE}/posts/${id}/feedback?feedback_tag=${encodeURIComponent(tag)}`, { method: 'POST' }).then(r => r.json()),

  // Content Calendar
  getCalendar: () => fetch(`${API_BASE}/calendar`).then(r => r.json()),
  generateCalendar: (payload) => fetch(`${API_BASE}/calendar/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(r => r.json()),
  updateCalendarItem: (id, data) => fetch(`${API_BASE}/calendar/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  // Research
  getResearch: () => fetch(`${API_BASE}/research`).then(r => r.json()),
  createResearch: (data) => fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  // Performance
  getPerformance: () => fetch(`${API_BASE}/performance`).then(r => r.json()),
  logPerformance: (data) => fetch(`${API_BASE}/performance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  getAnalyticsSummary: () => fetch(`${API_BASE}/performance/summary`).then(r => r.json()),

  // Exports
  getClipboard: (id) => fetch(`${API_BASE}/exports/clipboard/${id}`).then(r => r.json()),
  getMarkdownPackUrl: () => `${API_BASE}/exports/markdown-pack`,
  getSinglePdfUrl: (id) => `${API_BASE}/exports/pdf/${id}`,
  getPdfPackUrl: () => `${API_BASE}/exports/pdf-pack`,
  getCalendarCsvUrl: () => `${API_BASE}/exports/calendar-csv`,

  // System
  getStatus: () => fetch(`${API_BASE}/system/status`).then(r => r.json()),
  createBackup: () => fetch(`${API_BASE}/system/backup`, { method: 'POST' }).then(r => r.json()),
};
