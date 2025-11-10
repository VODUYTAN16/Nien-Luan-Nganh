// src/service.js
import api from '../axios';

const API_BASE = 'http://localhost:8000';

export function withBase(url) {
  if (!url) return url;
  if (url.startsWith('http')) return url;
  return API_BASE + url;
}

// Auth
export async function register(payload) {
  const res = await api.post('/auth/register', payload);
  return res.data;
}

export async function login(payload) {
  const res = await api.post('/auth/login', payload);
  const token = res.data?.access_token;
  if (token) {
    localStorage.setItem('access_token', token);
  }
  return res.data;
}

// Patterns
export async function fetchPatterns(params = {}) {
  const res = await api.get('/patterns', { params });
  return res.data; // array
}

export async function fetchPatternDetail(id) {
  const res = await api.get(`/patterns/${id}`);
  return res.data; // object
}

// Models (Model Lab)
export async function fetchModels() {
  const res = await api.get('/models');
  return res.data;
}

export async function setDefaultModel(code) {
  const res = await api.post(`/models/${code}/default`);
  return res.data;
}

// Search: text + ảnh, có chọn model
export async function searchPatterns({ modelCode, queryText, imageFile }) {
  const form = new FormData();
  form.append('model_code', modelCode);

  if (queryText) {
    form.append('query_text', queryText);
  }
  if (imageFile) {
    form.append('image', imageFile);
  }

  const res = await api.post('/search', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return res.data.items; // list SearchResultItem
}
